from odoo import api, fields, models
from odoo.exceptions import ValidationError

FIELD_TYPE = [
    ('integer', 'Số nguyên'),
    ('float', 'Số thực'),
    ('char', 'Kí tự'),
    ('text', 'Văn bản'),
    ('selection', 'Lựa chọn'),
    ('date', 'Ngày'),
    ('datetime', 'Ngày giờ'),
    ('binary', 'Tệp')
]


class DynamicField(models.Model):
    _name = 'dynamic.workflow.fields'
    _order = 'sequence'

    name = fields.Char('Tên trường', required=True)
    sequence = fields.Integer()
    help = fields.Text('Mô tả')
    is_required = fields.Boolean('Bắt buộc')
    field_id = fields.Many2one('ir.model.fields')
    stage_id = fields.Many2one('dynamic.workflow.stage', ondelete='cascade')
    field_type = fields.Selection(selection=FIELD_TYPE, string='Kiểu dữ liệu', required=True)
    selection_field = fields.Char(string="Các lựa chọn")
    selection_field_add = fields.Char(string="Thêm lựa chọn")
    is_used = fields.Boolean(related='stage_id.is_used')

    @api.model
    def create(self, values):
        res = super(DynamicField, self).create(values)
        if res.stage_id.workflow_id.is_used:
            raise ValidationError('Không thể tạo thêm trường khi quy trình đang được sử dụng.')
        field_name = 'x_truong_%s_%s' % (res.stage_id.id, res.id)
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'dynamic.workflow.task')])
        if res.is_required:
            class_color = 'color-required'
        else:
            class_color = 'color-default'

        inherit_id = self.env.ref('dynamic_workflow.dynamic_workflow_task_view_form')
        if res.field_type != 'binary':
            selection = []
            if res.field_type == 'selection':
                selection_value = res.selection_field.split(';')
                num = 1
                for select in selection_value:
                    selection.append(('selection_%s' % num, select.strip()))
                    num += 1
            field = self.env['ir.model.fields'].sudo().create({'name': field_name,
                                                               'field_description': res.name,
                                                               'model_id': model_id.id,
                                                               'ttype': res.field_type,
                                                               'is_required': res.is_required,
                                                               'help': res.help,
                                                               'selection': selection,
                                                               'is_dynamic': True,
                                                               'stage_id': res.stage_id.id
                                                               })
            arch_base = ('<?xml version="1.0"?>'
                         '<data>'
                         '<group name="dynamic_fields" position="inside">'
                         '<label for="%s" class="%s" invisible="%s not in stages_show_fields"/>'
                         '<field name="%s" nolabel="1" invisible="%s not in stages_show_fields" readonly="is_not_edit == True"/>'
                         '</group>'
                         '</data>') % (field_name, class_color, res.stage_id.id, field_name, res.stage_id.id)

        else:
            arch_base = ('<?xml version="1.0"?>'
                         '<data>'
                         '<group name="dynamic_fields" position="inside">'
                         '<label for="%s" class="%s" invisible="%s not in stages_show_fields"/>'
                         '<field name="%s" nolabel="1" invisible="%s not in stages_show_fields" widget="many2many_binary" readonly="is_not_edit == True"/>'
                         '</group>'
                         '</data>') % (field_name, class_color, res.stage_id.id, field_name, res.stage_id.id)

            field = self.env['ir.model.fields'].sudo().create({'name': field_name,
                                                               'field_description': res.name,
                                                               'model_id': model_id.id,
                                                               'ttype': 'many2many',
                                                               'is_required': res.is_required,
                                                               'help': res.help,
                                                               'relation': 'ir.attachment',
                                                               'is_dynamic': True,
                                                               'stage_id': res.stage_id.id
                                                               })


        view = self.env['ir.ui.view'].sudo().create({'name': 'dynamic.workflow.task.fields',
                                                     'type': 'form',
                                                     'model': 'dynamic.workflow.task',
                                                     'mode': 'extension',
                                                     'inherit_id': inherit_id.id,
                                                     'arch_base': arch_base,
                                                     'active': True})
        field.dynamic_view = view
        res.field_id = field
        return res

    def write(self, values):
        if 'selection_field_add' in values and values['selection_field_add']:
            values['selection_field'] = self.selection_field + '; ' + values['selection_field_add']
            values['selection_field_add'] = False
        res = super(DynamicField, self).write(values)
        selection = False
        if self.field_type == 'selection':
            selection = []
            selection_value = self.selection_field.split(';')
            num = 1
            for select in selection_value:
                selection.append(('selection_%s' % num, select.strip()))
                num += 1
        self.field_id.sudo().write({
            'field_description': self.name,
            'is_required': self.is_required,
            'selection': str(selection) if selection else False,
            'help': self.help
        })
        return res

    def unlink(self):
        for rec in self:
            if rec.stage_id.workflow_id.is_used:
                raise ValidationError('Không thể xóa trường khi quy trình đang được sử dụng.')
            rec.field_id.sudo().unlink()
        return super(DynamicField, self).unlink()


class WorkflowStage(models.Model):
    _name = 'dynamic.workflow.stage'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'name'
    _order = 'sequence, id'
    _description = 'Workflow stage'

    name = fields.Char('Tên', required=True, tracking=True)
    workflow_id = fields.Many2one('dynamic.workflow', string='Quy trình', ondelete="cascade", readonly=True)
    fold = fields.Boolean('Thu gọn')
    sequence = fields.Integer('Thứ tự')
    dynamic_field_ids = fields.One2many('dynamic.workflow.fields', 'stage_id', 'Trường tùy chỉnh', tracking=True)
    description = fields.Html(string="Mô tả")
    manager_ids = fields.Many2many('res.users', string='Người quản trị giai đoạn', tracking=True)
    follower_ids = fields.Many2many('res.users', 'follower_workflow_stage_rel', string='Người theo dõi giai đoạn',
                                    tracking=True)
    work_by_ids = fields.Many2many('res.users', 'work_by_workflow_stage_rel', string='Người thực hiện', tracking=True, required=True)
    assign_method = fields.Selection(string="Phương thức giao việc",
                                     selection=[
                                         ('keep', 'Giữ nguyên người nhận việc ở giai đoạn trước'),
                                         ('fist', 'Giao về cho người nhận nhiệm vụ đầu tiên'),
                                         ('not_assign', 'Không giao cho ai'),
                                         ('oneself', 'Để người nhận nhiệm vụ hiện tại quyết định'),
                                     ], required=True, default='oneself', tracking=True)
    work_time = fields.Float('Thời gian thực hiện (h)', tracking=True)
    type_set_work_time = fields.Selection(selection=[('static', 'Thời hạn cố định'),
                                                     ('dynamic', 'Thời hạn điều chỉnh')], required=True,
                                          default='static', tracking=True)
    type_back_stage = fields.Selection(selection=[('not_back', 'Không thể kéo ngược'),
                                                  ('most_recent', 'Chỉ có thể chuyển về giai đoạn trước'),
                                                  ('specifically', 'Chỉ có thể chuyển về giai đoạn cụ thể'),
                                                  ('any', 'Bất kì giai đoạn nào'),
                                                  ], string='Tùy chọn kéo ngược', required=True, default='not_back',
                                       tracking=True)
    back_stage_ids = fields.Many2many('dynamic.workflow.stage', 'back_stage_workflow_stage_rel',
                                      'stage_id', 'back_stage_id', string='Giai đoạn kéo ngược', tracking=True)
    is_done_stage = fields.Boolean()
    is_fail_stage = fields.Boolean()
    is_not_edit = fields.Boolean(related='workflow_id.is_not_edit')
    is_used = fields.Boolean(related='workflow_id.is_used')

    @api.constrains('dynamic_field_ids', 'sequence')
    def set_priority_view_dynamic_field_ids(self):
        for rec in self:
            num = 1
            for field in self.dynamic_field_ids:
                field.field_id.sudo().dynamic_view.priority = rec.sequence * 100 + num
                num += 1

    def action_show_details(self):
        self.ensure_one()
        return {
            "name": 'Giai đoạn',
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "dynamic.workflow.stage",
            "target": "new",
            "res_id": self.id,
        }

    def unlink(self):
        for rec in self:
            if rec.is_done_stage or rec.is_fail_stage:
                raise ValidationError('Không thể xóa giai đoạn mặc định')
        return super(WorkflowStage, self).unlink()
