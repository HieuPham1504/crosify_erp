# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CheckingPackedItemWizard(models.TransientModel):
    _name = 'checking.packed.item.wizard'

    item_ids = fields.One2many('checking.packed.item.line.item.wizard', 'checking_packed_item_wizard_id', 'Items')


    def action_packed_items(self):
        now = fields.Datetime.now()
        packed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.7')], limit=1)
        if not packed_level:
            raise ValidationError('There is no Packed Level')
        orders = self.item_ids.filtered(lambda line: line.state == 'pass' and line.type == 'order').mapped('order_ids')
        for item in orders.order_line:
            item.write({
                'packed_date': now,
                'sublevel_id': packed_level.id
            })

class CheckingPackedItemLineItemrWizard(models.TransientModel):
    _name = 'checking.packed.item.line.item.wizard'

    checking_packed_item_wizard_id = fields.Many2one('checking.packed.item.wizard')
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

    @api.onchange('barcode')
    def onchange_barcode(self):
        barcode = self.barcode
        Items = self.env['sale.order.line'].sudo()
        Orders = self.env['sale.order'].sudo()
        if barcode:
            item = Items.search([('production_id', '=', barcode)], limit=1)
            if item:
               data = {
                   'tkn_code': item.tkn_code,
                   'type': 'item',
                   'sale_order_line_id': item.id,
               }
               item_order_rel = self.checking_packed_item_wizard_id.item_ids.filtered(lambda item_line: not item_line.is_checked and item_line.type == 'order')
               item_order_rel_data = {}
               if item_order_rel:
                   if item_order_rel.tkn_code != item.tkn_code:
                       data.update({
                           'state': 'fail',
                           'line_item_id': item_order_rel.id,
                       })
               self.write(data)
               self.checking_packed_item_wizard_id.item_ids.filtered(lambda item_line: not item_line.is_checked and item_line.type == 'order').write(item_order_rel_data)
            else:
                orders = Orders.search([('order_id_fix', '=', barcode)])
                data = {
                    'order_ids': [(6, 0, orders.ids)],
                    'tkn_code': orders.mapped('tkn')[0],
                    'type': 'order',
                }
                self.write(data)
            return

    # @api.model_create_multi
    # def create(self, vals_list):
    #     remove_vals = []
    #     for val in vals_list:
    #         if not val.get('order_id'):
    #             remove_vals.append(val)
    #     for remove_val in remove_vals:
    #         vals_list.remove(remove_val)
    #     res = super(CheckingPackedItemLineOrderWizard, self).create(vals_list)
    #     return res

