# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ReadyPackingItemWizard(models.TransientModel):
    _name = 'ready.packing.item.wizard'
    _description = 'Ready To Pack'
    _rec_name = 'name'

    name = fields.Char(string='Name', default='Ready To Pack')
    line_ids = fields.One2many('ready.packing.item.line.wizard', 'ready_packing_item_wizard_id', string='Lines')

    def action_ready_to_pack_item(self):
        ready_to_pack_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.6')], limit=1)
        if not ready_to_pack_level:
            raise ValidationError('There is no Ready To Pack Level')
        Items = self.env['sale.order.line']
        pack_on_shelf_items = Items.sudo().search([('sublevel_id.level', '=', 'L4.5')])
        order_id_fixes = pack_on_shelf_items.mapped('order_id_fix')
        orders = self.env['sale.order'].sudo().search([('order_id_fix', 'in', order_id_fixes)])
        success_items = Items
        for order in orders:
            pack_on_shelf_item_orders = pack_on_shelf_items.filtered(lambda item: item.order_id == order)
            order_total_items = order.order_line
            if pack_on_shelf_item_orders == order_total_items:
                for item in pack_on_shelf_item_orders:
                    item.sublevel_id = ready_to_pack_level.id
                success_items += pack_on_shelf_item_orders
        line_datas = [{'sale_order_line_id': order_line.id} for order_line in success_items]
        line_ids = self.env['ready.packing.item.line.wizard'].create(line_datas)
        self.line_ids = [(6, 0, line_ids.ids)]

    def action_print_pdf_file(self):
        if not self.line_ids:
            raise ValidationError(_('No Data To Export PDF File'))
        try:
            data = [{
                'production_id': rec.production_id,
                'product_default_code': rec.product_id.default_code,
                'product_type': rec.product_type,
                'shelf_name': rec.address_shelf_id.shelf_name,
            } for rec in self.line_ids]
            item_data = {
                'items': data
            }
            report = self.env.ref('crosify_order.action_export_packing_item_barcode')
            report_action = report.report_action(self, data=item_data, config=False)
            report_action.update({'close_on_report_download': True})
            return report_action

        except (ValueError, AttributeError):
            raise ValidationError('Cannot Export into PDF File.')
class ReadyPackingItemLineWizard(models.TransientModel):
    _name = 'ready.packing.item.line.wizard'
    _order = 'production_id asc'

    ready_packing_item_wizard_id = fields.Many2one('ready.packing.item.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item')
    production_id = fields.Char(string='Production ID', related='sale_order_line_id.production_id')
    product_id = fields.Many2one('product.product', string='SKU', related='sale_order_line_id.product_id')
    address_shelf_id = fields.Many2one('fulfill.shelf', string='Address Shelf',
                                       related='sale_order_line_id.address_sheft_id')
    product_type = fields.Char(string='Product Type', related='sale_order_line_id.product_type')

