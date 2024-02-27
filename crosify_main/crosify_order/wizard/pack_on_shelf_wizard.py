# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackOnShelfWizard(models.TransientModel):
    _name = 'pack.on.shelf.wizard'

    address_shelf_id = fields.Many2one('fulfill.shelf', string='Address Shelf', required=True)
    line_ids = fields.One2many('pack.on.shelf.line.wizard', 'pack_on_shelf_wizard_id', string='Lines')

    def action_checking_item_shelf(self):
        pack_on_shelf_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.5')], limit=1)
        if not pack_on_shelf_level:
            raise ValidationError('There is no Pack On Shelf Level')
        for rec in self:
            lines = rec.line_ids
            main_address_shelf_id = rec.address_shelf_id
            diff_address_shelf_lines = lines.filtered(lambda line: line.address_shelf_id.id != main_address_shelf_id.id)
            same_address_shelf_lines = lines.filtered(lambda line: line.id not in diff_address_shelf_lines.ids)
            for same_line in same_address_shelf_lines:
                same_line.is_mismatch_shelf = False
            if diff_address_shelf_lines:
                production_ids = []
                for diff_line in diff_address_shelf_lines:
                    production_ids.append(diff_line.production_id)
                    diff_line.is_mismatch_shelf = True
                production_ids_str = ','.join(production_id for production_id in production_ids)
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'raise.information.wizard',
                    'views': [[self.env.ref('crosify_order.raise_information_wizard_form_view').id, 'form']],
                    'context': {
                        'default_warning': f'Mismatch Address Shelf With Production ID: {production_ids_str}'
                    },
                    'target': 'new',
                }
            else:
                for line in same_address_shelf_lines:
                    line.sale_order_line_id.sublevel_id = pack_on_shelf_level.id

class PackOnShelfLineWizard(models.TransientModel):
    _name = 'pack.on.shelf.line.wizard'
    _order = 'is_mismatch_shelf desc'

    @api.constrains('sale_order_line_id')
    def _check_sale_order_line_id(self):
        for record in self:
            sale_order_line_id = record.sale_order_line_id
            if sale_order_line_id.sublevel_id.level != 'L4.3':
                raise ValidationError(_("Only Transfer Item With QC Passed Level"))

    pack_on_shelf_wizard_id = fields.Many2one('pack.on.shelf.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item')
    production_id = fields.Char(string='Production ID', related='sale_order_line_id.production_id')
    product_id = fields.Many2one('product.product', string='SKU', related='sale_order_line_id.product_id')
    address_shelf_id = fields.Many2one('fulfill.shelf', string='Address Shelf', related='sale_order_line_id.address_sheft_id')
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', related='sale_order_line_id.sublevel_id')
    is_mismatch_shelf = fields.Boolean(string='Is Mismatch Shelf', default=False)

    @api.onchange('production_id')
    def onchange_production_id(self):
        production_id = self.production_id
        if production_id:
            duplicate_items = self.pack_on_shelf_wizard_id.line_ids.filtered(
                lambda item: item.production_id and item.production_id == production_id)
            if len(duplicate_items) > 1:
                return
            Items = self.env['sale.order.line'].sudo()
            item_id = Items.search([('production_id', '=', production_id)], limit=1)
            if item_id.sublevel_id.level != 'L4.3':
                raise ValidationError(_("Only Transfer Item With QC Passed Level"))
            if item_id:
                self.sale_order_line_id = item_id.id


