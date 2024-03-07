# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PickupItem(models.Model):
    _name = 'pickup.item'
    _rec_name = 'code'

    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id.id, required=True, index=True)
    note = fields.Text(string='Note')
    item_ids = fields.One2many('pickup.item.line', 'pickup_item_id', 'Deliver Items')

    @api.model_create_multi
    def create(self, vals_list):
        results = super(PickupItem, self).create(vals_list)

        for val in results:
            if not val.code:
                date = val.date
                time = date.strftime('%d/%m/%Y')
                today_format_split = time.split('/')
                date = today_format_split[0]
                month = today_format_split[1]
                year = today_format_split[-1][-2:]
                sequence = self.env['ir.sequence'].sudo().next_by_code('pickup.item') or ''
                code = f'PICKUP_{date}{month}{year}_{sequence}'
                val.code = code
        return results

    def action_pickup_items(self):
        now = fields.Datetime.now()
        pickup_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L5.1')], limit=1)
        if not pickup_level:
            raise ValidationError('There is no Pickup Level')
        total_items = self.item_ids
        if any(item.state == 'fail' for item in total_items):
            failed_items = total_items.filtered(lambda item: item.state == 'fail')
            tracking_code_faileds = list(set(failed_items.mapped('order_tracking_code')))
            total_items_fails = total_items.filtered(lambda item: item.order_tracking_code in tracking_code_faileds)
            total_order_fails = total_items.filtered(
                lambda item: item.tkn_code in tracking_code_faileds)
            total_fails = total_items_fails | total_order_fails
            for line in total_fails:
                line.write({
                    'is_fail_item': True,
                    'state': 'fail'
                })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'raise.information.wizard',
                'views': [[self.env.ref('crosify_order.raise_information_wizard_form_view').id, 'form']],
                'context': {
                    'default_warning': f'Can Not Packed Item With Fail Items'
                },
                'target': 'new',
            }

        order_lines_total = total_items.filtered(lambda line: line.type == 'order')
        orders = order_lines_total.order_ids
        for item in orders.order_line:
            item.write({
                'pickup_date': now,
                'shipping_date': now,
                'sublevel_id': pickup_level.id,
                'level_id': pickup_level.parent_id.id
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class PickupItemLine(models.Model):
    _name = 'pickup.item.line'
    _order = 'is_fail_item desc'

    pickup_item_id = fields.Many2one('pickup.item')
    barcode = fields.Char(string='Barcode')
    tkn_code = fields.Char(string='TKN Code')
    order_ids = fields.Many2many('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')
    is_checked = fields.Boolean(default=False)
    type = fields.Selection([
        ('item', 'Item'),
        ('order', 'Order')], string='Type')
    state = fields.Selection([
        ('fail', 'Fail'),
        ('pass', 'Pass')], string='State', default=False)
    order_tracking_code = fields.Char('Order Tracking Code')
    is_fail_item = fields.Boolean(default=False)

    @api.onchange('barcode')
    def onchange_barcode(self):
        barcode = self.barcode
        Items = self.env['sale.order.line'].sudo()
        Orders = self.env['sale.order'].sudo()
        if barcode:
            if len(barcode) > 30:
                barcode = barcode[8:]
            orders = Orders.search([('tkn', '=', barcode)])
            existed_order_line = self.pickup_item_id.item_ids.filtered(lambda line: line.type == 'order' and line.barcode == barcode)
            if not orders or existed_order_line:
                item = Items.search([('production_id', '=', barcode)], limit=1)
                if item.sublevel_id.level != 'L4.7':
                    raise ValidationError(_("Only Pickup Item With Packed Level"))
                if item:
                    data = {
                        'tkn_code': item.tkn_code,
                        'type': 'item',
                        'sale_order_line_id': item.id,
                    }
                    item_order_rel = self.pickup_item_id.item_ids.filtered(
                        lambda item_line: not item_line.is_checked and item_line.type == 'order')
                    if item_order_rel:
                        item_order_rel = item_order_rel[-1]
                        if item_order_rel.tkn_code != item.tkn_code:
                            data.update({
                                'state': 'fail',
                                'is_checked': True,
                                'order_tracking_code': item_order_rel.tkn_code,
                            })
                        else:
                            data.update({
                                'state': 'pass',
                                'is_checked': True,
                                'order_tracking_code': item_order_rel.tkn_code,
                            })
                    self.write(data)
            else:
                order_tkn = orders.mapped('tkn')[0]
                data = {
                    'order_ids': [(6, 0, orders.ids)],
                    'tkn_code': order_tkn,
                    'type': 'order',
                }
                items = self.pickup_item_id.item_ids.filtered(lambda line: line.type == 'item' and not line.is_checked and not line.state)
                if items:
                    tkn_code = items.mapped('tkn_code')[0]
                    data.update({
                        'order_tracking_code': tkn_code,
                        'state': 'pass' if order_tkn == tkn_code else 'fail'
                    })
                self.write(data)
        return

    @api.model_create_multi
    def create(self, vals_list):
        remove_vals = []
        for val in vals_list:
            if not val.get('barcode'):
                remove_vals.append(val)
        for remove_val in remove_vals:
            vals_list.remove(remove_val)
        res = super(PickupItemLine, self).create(vals_list)
        return res

