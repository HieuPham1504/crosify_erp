from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ShippingItemConfirm(models.Model):
    _name = 'shipping.item.confirm'
    _rec_name = 'code'

    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id.id, required=True, index=True)
    note = fields.Text(string='Note')
    item_ids = fields.One2many('shipping.item.confirm.line', 'shipping_item_confirm_id', 'Confirm Items')

    @api.model_create_multi
    def create(self, vals_list):
        results = super(ShippingItemConfirm, self).create(vals_list)

        for val in results:
            if not val.code:
                date = val.date
                time = date.strftime('%d/%m/%Y')
                today_format_split = time.split('/')
                date = today_format_split[0]
                month = today_format_split[1]
                year = today_format_split[-1][-2:]
                sequence = self.env['ir.sequence'].sudo().next_by_code('shipping.item.confirm') or ''
                code = f'CONFIRM_{date}{month}{year}_{sequence}'
                val.code = code
        return results

    def action_import_items(self):
        return

class ShippingItemConfirmLine(models.Model):
    _name = 'shipping.item.confirm.line'

    shipping_item_confirm_id = fields.Many2one('shipping.item.confirm')
    order_id_fix = fields.Char(string='Order ID Fix')
    tkn_code = fields.Char(string='TKN Code')