from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError


def timedelta_to_hours(time1, time2):
    time = time1 - time2
    day, hours, minutes = time.days, time.seconds // 3600, (time.seconds // 60) % 60
    to_hours = hours
    if day:
        to_hours += day * 24
    if minutes:
        to_hours += round(minutes / 60, 2)
    return to_hours


class WorkflowTaskProcess(models.Model):
    _name = 'workflow.task.process'

    task_id = fields.Many2one('dynamic.workflow.task', 'Nhiệm vụ', ondelete='cascade')
    stage_id = fields.Many2one('dynamic.workflow.stage', 'Giai đoạn')
    date_start = fields.Datetime(string="Thời gian bắt đầu")
    work_by_id = fields.Many2one('res.users', 'Người thực hiện')
    expected_time = fields.Float('Kỳ vọng (h)', related='stage_id.work_time')
    work_time_store = fields.Float('')
    real_time = fields.Float('Thực tế (h)', compute='_compute_real_time')

    def _compute_real_time(self):
        for rec in self:
            if rec.stage_id == rec.task_id.stage_id:
                work_time_append = timedelta_to_hours(datetime.now(), rec.task_id.date_start)
                rec.real_time = rec.work_time_store + work_time_append
            else:
                rec.real_time = rec.work_time_store


class WorkflowTaskJob(models.Model):
    _name = 'workflow.task.job'
    _order = 'stage_id'

    task_id = fields.Many2one('dynamic.workflow.task', 'Nhiệm vụ', ondelete='cascade')
    description = fields.Html('Mô tả công việc', required=True)
    is_done = fields.Boolean('Hoàn thành')
    stage_id = fields.Many2one('dynamic.workflow.stage', 'Giai đoạn', readonly=True)

    @api.model
    def create(self, values):
        res = super(WorkflowTaskJob, self).create(values)
        res.stage_id = res.task_id.stage_id
        return res


class WorkflowTask(models.Model):
    _name = 'dynamic.workflow.task'
    _rec_name = 'name'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Nhiệm vụ'

    def _default_stage_id(self):
        if 'default_workflow_id' in self.env.context:
            return self.env['dynamic.workflow'].sudo().browse(self.env.context['default_workflow_id']).stage_ids[0]
        return False

    name = fields.Char('Tên', required=True, tracking=True)
    workflow_id = fields.Many2one('dynamic.workflow', string='Quy trình', readonly=True, tracking=True)
    stage_id = fields.Many2one('dynamic.workflow.stage', string='Giai đoạn', group_expand='_read_group_stage_ids',
                               domain="[('workflow_id', '=', workflow_id)]", readonly=True,
                               default=_default_stage_id, tracking=True)
    priority = fields.Boolean()
    stages_show_fields = fields.Many2many('dynamic.workflow.stage', compute='_compute_stages_show_fields')
    work_by_domain = fields.Many2many('res.users', related='stage_id.work_by_ids')
    work_by_id = fields.Many2one('res.users', 'Người thực hiện', tracking=True)
    description = fields.Html('Mô tả nhiệm vụ')
    follower_ids = fields.Many2many('res.users', 'follower_workflow_task_rel', string='Người theo dõi', tracking=True)
    task_process = fields.One2many('workflow.task.process', 'task_id', string='Tiến trình', tracking=True)
    job_ids = fields.One2many('workflow.task.job', 'task_id', string='Công việc', tracking=True)
    date_start = fields.Datetime('Thời gian bắt đầu', readonly=True, default=datetime.now(), tracking=True)
    date_end = fields.Datetime('Thời gian đến hạn', tracking=True)
    bg_color = fields.Selection(string="Màu",
                                selection=[('fail', 'bg-fail'), ('success', 'bg-success'), ('warning', 'bg-warning')],
                                compute='_compute_bg_color')
    type_set_work_time = fields.Selection(related='stage_id.type_set_work_time')
    is_hide_back = fields.Boolean(compute='_compute_is_hide_back')
    is_hide_next = fields.Boolean(compute='_compute_is_hide_next')
    is_hide_fail = fields.Boolean(compute='_compute_is_hide_fail')
    stage_description = fields.Html(related='stage_id.description')
    fail_reason = fields.Char(readonly=True)
    is_not_edit = fields.Boolean(compute='_compute_is_not_edit')

    def _compute_is_not_edit(self):
        for rec in self:
            if rec.stage_id.is_done_stage or rec.stage_id.is_fail_stage:
                rec.is_not_edit = True
            else:
                user_can_edit = rec.workflow_id.manager_ids + rec.work_by_id + rec.workflow_id.department_ids.member_ids.user_id
                if self.env.uid in user_can_edit.ids or self.env.user.has_group(
                        'dynamic_workflow.group_workflow_manager'):
                    rec.is_not_edit = False
                else:
                    rec.is_not_edit = True

    def _compute_bg_color(self):
        for rec in self:
            if rec.stage_id.is_done_stage:
                rec.bg_color = 'success'
            elif rec.stage_id.is_fail_stage:
                rec.bg_color = 'fail'
            elif rec.date_end and rec.date_end < datetime.now():
                rec.bg_color = 'warning'
            else:
                rec.bg_color = False

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end and self.date_end < self.date_start:
            raise UserError('Thời gian đến hạn phải lớn hơn thời gian bắt đầu')

    def _compute_is_hide_fail(self):
        for rec in self:
            if (
                    self.env.uid == rec.work_by_id.id or self.env.uid in rec.workflow_id.manager_ids.ids or self.env.user.has_group(
                'dynamic_workflow.group_workflow_manager')) and (
                    not rec.stage_id.is_done_stage and not rec.stage_id.is_fail_stage):
                rec.is_hide_fail = False
            else:
                rec.is_hide_fail = True

    def _compute_is_hide_next(self):
        for rec in self:
            if (
                    self.env.uid == rec.work_by_id.id or self.env.uid in rec.workflow_id.manager_ids.ids or self.env.user.has_group(
                'dynamic_workflow.group_workflow_manager')) and (
                    not rec.stage_id.is_done_stage and not rec.stage_id.is_fail_stage):
                rec.is_hide_next = False
            else:
                rec.is_hide_next = True

    def _compute_is_hide_back(self):
        for rec in self:
            if (
                    self.env.uid == rec.work_by_id.id or self.env.uid in rec.workflow_id.manager_ids.ids or self.env.user.has_group(
                'dynamic_workflow.group_workflow_manager')) and rec.stage_id != rec.workflow_id.stage_ids[0]:
                if rec.stage_id.type_back_stage == 'not_back':
                    rec.is_hide_back = True
                else:
                    rec.is_hide_back = False
            else:
                rec.is_hide_back = True

    @api.model
    def default_get(self, fields_list):
        res = super(WorkflowTask, self).default_get(fields_list)
        vals = []
        if 'default_workflow_id' in self.env.context:
            workflow_id = self.env['dynamic.workflow'].sudo().browse(self.env.context['default_workflow_id'])
            for stage_id in workflow_id.stage_ids:
                if not stage_id.is_done_stage and not stage_id.is_fail_stage:
                    vals.append((0, 0, {'stage_id': stage_id.id}))
            res.update({'task_process': vals})
        return res

    @api.constrains('stage_id')
    def _constrains_stage_id(self):
        self.date_start = datetime.now()
        if self.stage_id.work_time:
            self.date_end = self.date_start + timedelta(hours=self.stage_id.work_time)

    @api.constrains('work_by_id')
    def constrains_work_by_id(self):
        task_process_id = self.task_process.filtered(lambda r: r.stage_id == self.stage_id)
        if task_process_id:
            task_process_id.work_by_id = self.work_by_id

    @api.depends('workflow_id')
    def _compute_stages_show_fields(self):
        for rec in self:
            next_stage = self.env['dynamic.workflow.stage'].sudo().search([('sequence', '>', self.stage_id.sequence),
                                                                           ('workflow_id', '=', self.workflow_id.id)],
                                                                          limit=1, order='sequence asc')
            stage_show_fields = self.env['dynamic.workflow.stage'].sudo().search(
                [('sequence', '<=', self.stage_id.sequence),
                 ('workflow_id', '=', self.workflow_id.id)])
            rec.stages_show_fields = stage_show_fields + next_stage

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        if 'default_workflow_id' in self.env.context:
            search_domain = [('workflow_id', '=', self.env.context['default_workflow_id'])]
        stage_ids = stages._search(search_domain, order='sequence', access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def action_fail(self):
        return {
            'name': 'Lí do thất bại',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.fail.reason',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_task_id': self.id
            }
        }

    def action_next_stage(self):
        next_stage = self.env['dynamic.workflow.stage'].sudo().search([('sequence', '>', self.stage_id.sequence),
                                                                       ('workflow_id', '=', self.workflow_id.id)],
                                                                      limit=1, order='sequence asc')
        dynamic_fields_required = self.env['ir.model.fields'].sudo().search(
            [('stage_id.sequence', '<=', next_stage.sequence),
             ('is_required', '=', True),
             ('stage_id.workflow_id', '=', self.workflow_id.id)])

        message = ''
        for field in dynamic_fields_required:
            if self.sudo().search([(field.name, '=', False), ('id', '=', self.id), ]):
                message += field.field_description + ', '

        if message:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Trường tùy chỉnh bắt buộc:',
                    'message': message[:-2],
                    'sticky': False,
                    'type': 'danger',
                }
            }
        if next_stage.assign_method == 'first':
            self.work_by_id = self.work_by_id
        elif next_stage.assign_method == 'not_assign':
            self.work_by_id = False
        elif next_stage.assign_method == 'first':
            first_stage = self.workflow_id.stage_ids[0]
            first_user = self.task_process.filtered(lambda r: r.stage_id == first_stage.id).work_by_id
            self.work_by_id = first_user
        elif next_stage.assign_method == 'oneself':
            return {
                'name': 'Giao việc',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'assign.task',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_stage_id': next_stage.id,
                    'default_task_id': self.id
                }
            }
        self.stage_id = next_stage
        self.constrains_work_by_id()

    def action_back_stage(self):
        back_stage = self.env['dynamic.workflow.stage'].sudo().search([('sequence', '<', self.stage_id.sequence),
                                                                       ('workflow_id', '=', self.workflow_id.id)],
                                                                      limit=1, order='sequence desc')
        if self.stage_id.type_back_stage in ['specifically', 'any']:
            return {
                'name': 'Giai đoạn kéo lùi',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'back.stage',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_stage_id': self.stage_id.id,
                    'default_task_id': self.id,
                }
            }
        self.stage_id = back_stage


    @api.model
    def create(self, values):
        values['date_start'] = datetime.now()

        res = super(WorkflowTask, self).create(values)
        attachment_ids = self.env['ir.attachment'].sudo().search([('create_uid', '=', self.env.uid),
                                                                ('res_model', '=', 'dynamic.workflow.task'),
                                                                ('res_id', '=', 0)])
        for attachment_id in attachment_ids:
            attachment_id.write({'res_model': res._name, 'res_id': res.id})
        return res

    def write(self, values):
        if 'stage_id' in values:
            if values['stage_id'] != self.stage_id.id:
                work_time_append = timedelta_to_hours(datetime.now(), self.date_start)
                self.task_process.filtered(lambda r: r.stage_id == self.stage_id).work_time_store += work_time_append
        res = super(WorkflowTask, self).write(values)
        return res
