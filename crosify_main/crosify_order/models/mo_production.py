from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MOProduction(models.Model):
    _name = 'mo.production'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production'
    _rec_name = 'code'
    _order = 'date desc'

    code = fields.Char(string='Code')
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=lambda self: self.env.user.employee_id.id)
    note = fields.Text(string='Note')
    mo_production_line_ids = fields.Many2many('sale.order.line', 'mo_production_so_line_rel', string='Items')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('production', 'Production')
    ], string='State', default='draft', index=True, tracking=1)

    @api.constrains('mo_production_line_ids')
    def constraint_sale_order_line_id(self):
        for rec in self:
            for item in rec.mo_production_line_ids:
                duplicate_item = self.sudo().search(
                    [('mo_production_line_ids', 'in', item.ids), ('id', '!=', rec.id)])
                if duplicate_item:
                    raise ValidationError(
                        _(f"This Item {item.display_name} already exists in Productions {','.join(code for code in duplicate_item.mapped('code'))}"))

    @api.model_create_multi
    def create(self, vals_list):
        results = super(MOProduction, self).create(vals_list)
        for val in results:
            if not val.code:
                val.code = self.env['ir.sequence'].sudo().next_by_code('mo.production.code') or _('New')
        return results

    def action_set_item_start_info(self):
        for line in self.mo_production_line_ids:
            data = {}
            if self.date:
                data.update({
                    'production_start_date': self.date
                })
            if self.note:
                data.update({
                    'production_note': self.note
                })
            line.write(data)

    def action_produce_items(self):
        production_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.1')], limit=1)
        if not production_level:
            raise ValidationError('There is no state with level Production')
        for rec in self:
            if not rec.mo_production_line_ids:
                continue
            for item in rec.mo_production_line_ids:
                item.write({
                    'sublevel_id': production_level.id,
                    'level_id': production_level.parent_id.id,
                })
            rec.action_set_item_start_info()
            rec.state = 'production'

    def action_back_to_designed_items(self):
        designed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L3.2')], limit=1)
        if not designed_level:
            raise ValidationError('There is no state with level Designed')
        for rec in self:
            for item in rec.mo_production_line_ids:
                item.write({
                    'sublevel_id': designed_level.id,
                    'level_id': designed_level.parent_id.id,
                    'production_start_date': False
                })
            rec.state = 'draft'


