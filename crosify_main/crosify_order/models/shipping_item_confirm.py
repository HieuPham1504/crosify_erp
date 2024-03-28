from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import openpyxl
import base64
from io import BytesIO


class ShippingItemConfirm(models.Model):
    _name = 'shipping.item.confirm'
    _description = 'Shipping Item Confirm'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True, tracking=1)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id.id,
                                  required=True, index=True, tracking=1)
    note = fields.Text(string='Note')
    item_ids = fields.One2many('shipping.item.confirm.line', 'shipping_item_confirm_id', 'Confirm Items')
    delivered_item_file = fields.Binary(string='Delivered Items File')
    delivered_item_file_name = fields.Char(string='Delivered')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], string='State', default="draft", index=True, tracking=1)


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

    def unlink(self):
        current_user = self.env.user
        operator_user = current_user.has_group('crosify_order.group_sale_team_operator')
        system_user = current_user.has_group('base.group_system')
        if operator_user or system_user:
            if any([rec.state != 'draft' for rec in self]):
                raise ValidationError(_('Can Not Delete Record'))
        else:
            raise ValidationError(_('Can Not Delete Record'))
        res = super().unlink()
        return res

    def action_import_items(self):
        Orders = self.env['sale.order'].sudo()
        ItemLines = self.env['shipping.item.confirm.line'].sudo()
        import_file = self.delivered_item_file
        try:
            wb = openpyxl.load_workbook(

                filename=BytesIO(base64.b64decode(import_file)), read_only=True
            )
            item_file_datas = []
            order_id_fixes = []
            ws = wb.active
            for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,
                                       max_col=None, values_only=True):
                order_id_fix = str(record[1])
                order_id_fix = order_id_fix.strip()
                if order_id_fix and order_id_fix not in order_id_fixes:
                    order_id_fixes.append(order_id_fix)
                    order = Orders.search([('order_id_fix', '=', order_id_fix), ('tkn', '!=', False)], limit=1)
                    if order:
                        item_file_datas.append({
                            'order_id_fix': order_id_fix,
                            'tkn_code': order.tkn,
                            'shipping_item_confirm_id': self.id,
                        })

            item_ids = ItemLines.create(item_file_datas)
            self.item_ids = [(6, 0, item_ids.ids)]

        except:
            raise ValidationError(_('Insert Invalid File'))

    def action_confirm_item(self):
        Levels = self.env['sale.order.line.level'].sudo()
        Orders = self.env['sale.order'].sudo()
        ShippingLines = self.env['shipping.item.confirm.line'].sudo()
        pickup_level = Levels.search([('level', '=', 'L5.1')], limit=1)
        shipping_confirm_level = Levels.search([('level', '=', 'L5.2')], limit=1)
        if not pickup_level:
            raise ValidationError('There is no state with level Pickup')
        if not pickup_level:
            raise shipping_confirm_level('There is no state with level Shipping Confirm')

        item_ids = self.item_ids
        order_id_fixes = list(set(item_ids.mapped('order_id_fix')))
        items = self.env['sale.order.line'].sudo().search([('order_id_fix', 'in', order_id_fixes), ('is_create_so_rp', '=', False)])
        wrong_level_items = items.filtered(lambda item: item.sublevel_id.id != pickup_level.id)

        if len(wrong_level_items) > 0:
            order_id_fixes = list(set(wrong_level_items.mapped('order_id_fix')))
            order_id_fixes_str = ','.join(order_id_fixes)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'raise.information.wizard',
                'views': [[self.env.ref('crosify_order.raise_information_wizard_form_view').id, 'form']],
                'context': {
                    'default_warning': f'Can not Confirm Item With Order ID Fix: {order_id_fixes_str}'
                },
                'target': 'new',
            }

        else:
            for item in items:
                item.write({
                    'sublevel_id': shipping_confirm_level.id,
                    'shipping_confirm_date': datetime.now().date(),
                })
            self.state = 'done'



class ShippingItemConfirmLine(models.Model):
    _name = 'shipping.item.confirm.line'

    shipping_item_confirm_id = fields.Many2one('shipping.item.confirm', ondelete='cascade')
    order_id_fix = fields.Char(string='Order ID Fix')
    tkn_code = fields.Char(string='TKN Code')

