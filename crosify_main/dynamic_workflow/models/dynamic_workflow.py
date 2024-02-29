from odoo import api, fields, models


class WorkflowFailReason(models.Model):
    _name = 'fail.reason'
    _rec_name = 'name'

    name = fields.Char('Lí do thất bại')
    workflow_id = fields.Many2one('dynamic.workflow', ondelete='cascade')

class DynamicWorkflow(models.Model):
    _name = 'dynamic.workflow'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Quy trình'
    _order = 'is_favorite'

    active = fields.Boolean(default=True)
    name = fields.Char('Tên luồng công việc', required=True, tracking=True)
    manager_ids = fields.Many2many('res.users', string='Thành viên quản trị',
                                   required=True,
                                   tracking=True,
                                   default=lambda self: [self.env.uid],
                                   help='Người quản trị có thể xem nhiệm vụ của mọi thành viên. Bạn được mặc định là một người quản trị')
    department_ids = fields.Many2many('hr.department', string='Nhóm tạo nhiệm vụ mới')
    type = fields.Char('Phân loại luồng công việc', tracking=True)
    task_ids = fields.One2many('dynamic.workflow.task', 'workflow_id', string='Công việc')
    stage_ids = fields.One2many('dynamic.workflow.stage', 'workflow_id', string='Giai đoạn', tracking=True)
    is_favorite = fields.Boolean('Favorite')
    department_view_workflow_ids = fields.Many2many('hr.department', 'department_view_workflow_rel',
                                                    string='Nhóm xem quy trình', tracking=True)
    description = fields.Html('Mô tả quy trình', tracking=True)
    supervisor = fields.Many2many('res.users', 'dynamic_workflow_supervisor_rel', string='Người giám sát',
                                  help='Thành viên có quyền xem & review tất cả nhiệm vụ nhưng không có quyền chỉnh sửa', tracking=True)
    type_view_task = fields.Selection(string="Hiển thị nhiệm vụ", selection=[('all', 'Tất cả nhiệm vụ'),
                                                                             ('only', 'Chỉ thành viên theo dõi')],
                                      required=True, tracking=True, help='Quyền xem các nhiệm vụ trong luồng công việc',
                                      default='all')
    is_used = fields.Boolean(compute='_compute_is_used')
    fail_reason_ids = fields.One2many('fail.reason', 'workflow_id', tracking=True)
    is_not_edit = fields.Boolean(compute='_compute_is_not_edit')

    def _compute_is_not_edit(self):
        for rec in self:
            if self.env.uid in rec.manager_ids.ids or self.env.user.has_group(
                    'dynamic_workflow.group_workflow_manager'):
                rec.is_not_edit = False
            else:
                rec.is_not_edit = True

    def _compute_is_used(self):
        for rec in self:
            if self.env['dynamic.workflow.task'].sudo().search_count([('workflow_id', '=', rec.id)]):
                rec.is_used = True
            else:
                rec.is_used = False

    def action_view_tasks(self):
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id(
            'dynamic_workflow.act_dynamic_workflow_task_all')
        action['display_name'] = self.name
        context = action['context'].replace('active_id', str(self.id))
        action['context'] = context
        return action

    @api.constrains('stage_ids')
    def _constrains_stage_ids(self):
        self.stage_ids.filtered(lambda r: r.is_done_stage).sequence = len(self.stage_ids) + 1
        self.stage_ids.filtered(lambda r: r.is_fail_stage).sequence = len(self.stage_ids) + 2

    @api.model
    def create(self, values):
        res = super(DynamicWorkflow, self).create(values)
        sequence = len(res.stage_ids)
        self.env['dynamic.workflow.stage'].sudo().create({
            'name': 'Hoàn thành',
            'is_done_stage': True,
            'sequence': sequence + 1,
            'workflow_id': res.id,
            'assign_method': 'keep'
        })
        self.env['dynamic.workflow.stage'].sudo().create({
            'name': 'Thất bại',
            'is_fail_stage': True,
            'sequence': sequence + 2,
            'workflow_id': res.id,
            'assign_method': 'keep'
        })
        return res
