# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CheckingPackedItemWizard(models.TransientModel):
    _name = 'checking.packed.item.wizard'

    order_ids = fields.One2many('checking.packed.item.line.order.wizard', 'checking_packed_item_wizard_id', 'Orders')
    item_ids = fields.One2many('checking.packed.item.line.item.wizard', 'checking_packed_item_wizard_id', 'Items')

    # @api.onchange('order_ids')
    # def onchange_order_ids(self):
    #     order_ids = self.order_ids
    #     line_datas = [{'sale_order_line_id': line.id} for line in order_ids.order_line]
    #     item_line_ids = self.env['checking.packed.item.line.item.wizard'].create(line_datas)
    #     self.item_ids = [(6, 0, item_line_ids.ids)]

class CheckingPackedItemLineItemrWizard(models.TransientModel):
    _name = 'checking.packed.item.line.item.wizard'

    checking_packed_item_wizard_id = fields.Many2one('checking.packed.item.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line')
    order_id_fix = fields.Char(string='Order ID Fix', related='sale_order_line_id.order_id_fix')
    production_id = fields.Char(string='Order ID Fix', related='sale_order_line_id.production_id')
    product_id = fields.Many2one('product.product', string='SKU', related='sale_order_line_id.product_id')
    sublevel_id = fields.Many2one('sale.order.line.level', related='sale_order_line_id.sublevel_id')


class CheckingPackedItemLineOrderWizard(models.TransientModel):
    _name = 'checking.packed.item.line.order.wizard'

    checking_packed_item_wizard_id = fields.Many2one('checking.packed.item.wizard')
    order_name = fields.Char(string='Order Name', required=True)
    order_id = fields.Many2one('sale.order', string='Order')

    @api.onchange('order_name')
    def onchange_order_name(self):
        order_name = self.order_name
        if order_name:
            order_name = order_name.replace('TEST', '')
            sale_order = self.env['sale.order'].sudo().search([('name', '=', order_name)], limit=1)
            if sale_order:
                self.write({
                    'order_id': sale_order.id,
                    'order_name': order_name,
                })

            order_ids = self.checking_packed_item_wizard_id.order_ids
            line_datas = [{'sale_order_line_id': line.id} for line in order_ids.order_id.order_line]
            item_line_ids = self.env['checking.packed.item.line.item.wizard'].create(line_datas)
            self.checking_packed_item_wizard_id.item_ids = [(6, 0, item_line_ids.ids)]
