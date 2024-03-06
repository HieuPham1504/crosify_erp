
# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackedItemWizard(models.TransientModel):
    _name = 'packed.item.wizard'
    _rec_name = 'name'

    name = fields.Char(string='Packed Item')
    item_ids = fields.One2many('packed.item.line.wizard', 'packed_item_wizard_id', 'Items')

    def action_pakced_item(self):
        now = datetime.now()
        items = self.item_ids
        Levels = self.env['sale.order.line.level'].sudo()
        packed_level = Levels.search([('level', '=', 'L4.7')])
        pending_level = Levels.search([('level', '=', 'L7.4')])
        for item in items:
            is_upload_tkn = item.is_upload_tkn
            if is_upload_tkn:
                if not packed_level:
                    raise ValidationError('There is no state with level Packed')
                item.write({
                    'sublevel_id': packed_level.id,
                    'packed_date': now
                })
            else:
                if not pending_level:
                    raise ValidationError('There is no state with level Pending')
                item.sublevel_id = pending_level.id



class PackedItemLineWizard(models.TransientModel):
    _name = 'packed.item.line.wizard'

    packed_item_wizard_id = fields.Many2one('packed.item.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line', required=False, string='Item')
    production_id = fields.Char(string='Production ID', required=True, index=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', store=True, index=True)
    product_template_attribute_value_ids = fields.Many2many(
        related='sale_order_line_id.product_template_attribute_value_ids')
    personalize = fields.Char(string='Personalize', related='sale_order_line_id.personalize', store=True)

    @api.onchange('production_id')
    def onchange_production_id(self):
        production_id = self.production_id
        if production_id:
            duplicate_items = self.packed_item_wizard_id.item_ids.filtered(
                lambda item: item.production_id and item.production_id == production_id)
            if len(duplicate_items) > 1:
                return
            Items = self.env['sale.order.line'].sudo()
            item_id = Items.search([('production_id', '=', production_id)], limit=1)
            if item_id.sublevel_id.level != 'L4.6':
                raise ValidationError(_("Only Transfer Item With QC Passed Level"))
            if item_id:
                self.sale_order_line_id = item_id.id

    @api.model_create_multi
    def create(self, vals_list):
        remove_vals = []
        for val in vals_list:
            if not val.get('sale_order_line_id'):
                remove_vals.append(val)
        for remove_val in remove_vals:
            vals_list.remove(remove_val)
        res = super(PackedItemLineWizard, self).create(vals_list)
        return res
