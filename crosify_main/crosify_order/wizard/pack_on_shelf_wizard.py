# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackOnShelfWizard(models.TransientModel):
    _name = 'pack.on.shelf.wizard'

    line_ids = fields.One2many('pack.on.shelf.line.wizard', 'pack_on_shelf_wizard_id', string='Lines')

    def action_checking_item_shelf(self):
        pack_on_shelf_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.5')], limit=1)
        if not pack_on_shelf_level:
            raise ValidationError('There is no Pack On Shelf Level')
        for rec in self:
            total_lines = rec.line_ids
            total_shelfs = total_lines.filtered(lambda line: line.type == 'shelf')

            for shelf in total_shelfs:
                pair_number = shelf.pair_number
                new_address_shelf_id = shelf.new_address_shelf_id

                items_in_shelf = total_lines.filtered(lambda
                                                         line: line.type == 'item' and line.pair_number == pair_number)

                for item in items_in_shelf:
                    data = {
                        'sublevel_id': pack_on_shelf_level.id,
                        'level_id': pack_on_shelf_level.parent_id.id,
                    }
                    if item.old_address_shelf_id.id != new_address_shelf_id.id:
                        data.update({
                            'address_sheft_id': new_address_shelf_id.id
                        })
                    item.sale_order_line_id.write(data)

class PackOnShelfLineWizard(models.TransientModel):
    _name = 'pack.on.shelf.line.wizard'
    _order = 'is_mismatch_shelf desc'

    pack_on_shelf_wizard_id = fields.Many2one('pack.on.shelf.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item')
    barcode = fields.Char(string='Barcode', required=True)
    product_id = fields.Many2one('product.product', string='SKU', related='sale_order_line_id.product_id')
    old_address_shelf_id = fields.Many2one('fulfill.shelf', string='Address Shelf',
                                           related='sale_order_line_id.address_sheft_id')
    new_address_shelf_id = fields.Many2one('fulfill.shelf', string='New Address Shelf')
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', related='sale_order_line_id.sublevel_id')
    is_mismatch_shelf = fields.Boolean(string='Is Mismatch Shelf', default=False)
    pair_number = fields.Integer(string='Pair Number')
    type = fields.Selection([
        ('shelf', 'Shelf'),
        ('item', 'Item')], string='Type')

    @api.onchange('barcode')
    def onchange_barcode(self):
        barcode = self.barcode
        if barcode:
            total_lines = self.pack_on_shelf_wizard_id.line_ids

            duplicate_items = total_lines.filtered(
                lambda item: item.barcode and item.barcode == barcode)
            if len(duplicate_items) > 1:
                raise ValidationError(_('Duplicate Barcode'))
            Items = self.env['sale.order.line'].sudo()
            FulfillShelfs = self.env['fulfill.shelf'].sudo()

            new_address_shelf_id = FulfillShelfs.search([('shelf_code', '=', barcode)], limit=1)
            if new_address_shelf_id:
                pair_numbers = total_lines.mapped('pair_number')
                new_pair_number = 1
                if len(pair_numbers) > 0:
                    new_pair_number = max(pair_numbers) + 1
                self.write({
                    'barcode': barcode,
                    'new_address_shelf_id': new_address_shelf_id.id,
                    'pair_number': new_pair_number,
                    'type': 'shelf',
                })
            else:
                item_id = Items.search([('production_id', '=', barcode)], limit=1)
                if item_id:
                    if item_id.sublevel_id.level != 'L4.3':
                        raise ValidationError(_("Only Transfer Item With QC Passed Level"))
                    nearest_shelf = total_lines.filtered(lambda line: line.type == 'shelf')
                    if not nearest_shelf:
                        raise ValidationError(_('Address Shelf Not Found'))
                    nearest_shelf = nearest_shelf[-1]
                    shelf_pair_number = nearest_shelf.pair_number
                    self.write({
                        'barcode': barcode,
                        'pair_number': shelf_pair_number,
                        'sale_order_line_id': item_id.id,
                        'type': 'item',
                    })

