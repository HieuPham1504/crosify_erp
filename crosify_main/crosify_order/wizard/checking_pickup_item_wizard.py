# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CheckingPackedItemWizard(models.TransientModel):
    _name = 'checking.pickup.item.wizard'
    _rec_name = 'name'

    name = fields.Char(string='Pickup Item')
    item_ids = fields.One2many('checking.pickup.item.line.item.wizard', 'checking_pickup_item_wizard_id', 'Items')

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
                'level_id': pickup_level.parent_Id.id
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class CheckingPackedItemLineItemrWizard(models.TransientModel):
    _name = 'checking.pickup.item.line.item.wizard'
    _order = 'is_fail_item desc'

    checking_pickup_item_wizard_id = fields.Many2one('checking.pickup.item.wizard')
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
            orders = Orders.search([('order_id_fix', '=', barcode)])
            existed_order_line = self.checking_pickup_item_wizard_id.item_ids.filtered(lambda line: line.type == 'order' and line.barcode == barcode)
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
                    item_order_rel = self.checking_pickup_item_wizard_id.item_ids.filtered(
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
                items = self.checking_pickup_item_wizard_id.item_ids.filtered(lambda line: line.type == 'item' and not line.is_checked and not line.state)
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
        res = super(CheckingPackedItemLineItemrWizard, self).create(vals_list)
        return res
