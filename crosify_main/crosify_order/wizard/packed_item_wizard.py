# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackedItemWizard(models.TransientModel):
    _name = 'packed.item.wizard'
    _rec_name = 'name'

    name = fields.Char(string='Name', default='Packed Item')
    item_ids = fields.One2many('packed.item.line.wizard', 'packed_item_wizard_id', 'Items')

    def action_pakced_item(self):
        Items = self.env['sale.order.line'].sudo()
        now = datetime.now()
        items = self.item_ids

        order_id_fixes = list(set(items.mapped('order_id_fix')))
        error_items = Items
        for order_id_fix in order_id_fixes:
            item_groups = items.filtered(lambda item: item.order_id_fix == order_id_fix)
            item_order_lines = item_groups.mapped('sale_order_line_id')

            total_items = Items.search([('order_id_fix', '=', order_id_fix), ('is_create_so_rp', '=', False)])

            if item_order_lines != total_items:
                for error_item in item_groups:
                    error_item.is_error = True
                error_items |= item_order_lines
            else:
                pair_items = item_groups.mapped('pair_number')
                if len(set(pair_items)) > 1:
                    for error_item in item_groups:
                        error_item.is_error = True
                    error_items |= item_order_lines

        if len(error_items) > 0:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'raise.information.wizard',
                'views': [[self.env.ref('crosify_order.raise_information_wizard_form_view').id, 'form']],
                'context': {
                    'default_warning': f'Can Not Packed Item'
                },
                'target': 'new',
            }

        Levels = self.env['sale.order.line.level'].sudo()
        packed_level = Levels.search([('level', '=', 'L4.7')])
        pending_level = Levels.search([('level', '=', 'L7.4')])
        for item in items.mapped('sale_order_line_id'):
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

        items.unlink()


class PackedItemLineWizard(models.TransientModel):
    _name = 'packed.item.line.wizard'

    packed_item_wizard_id = fields.Many2one('packed.item.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line', required=False, string='Item')
    production_id = fields.Char(string='Production ID', required=True, index=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', store=True, index=True)
    order_id_fix = fields.Char(related='sale_order_line_id.order_id_fix', store=True, index=True)
    product_template_attribute_value_ids = fields.Many2many(
        related='sale_order_line_id.product_template_attribute_value_ids')
    personalize = fields.Char(string='Personalize', related='sale_order_line_id.personalize', store=True)
    is_error = fields.Boolean(string='Is Error')
    error_message = fields.Char(string='Status', compute='_compute_error_message')
    pair_number = fields.Integer(string='Pair Number')


    @api.depends('is_error')
    def _compute_error_message(self):
        for rec in self:
            error_message = 'Missing Item' if rec.is_error else False
            rec.error_message = error_message

    @api.onchange('production_id')
    def onchange_production_id(self):
        production_id = self.production_id
        if production_id:
            total_items = self.packed_item_wizard_id.item_ids

            duplicate_items = self.packed_item_wizard_id.item_ids.filtered(
                lambda item: item.production_id and item.production_id == production_id)
            if len(duplicate_items) > 1:
                raise ValidationError(_('Duplicate Production ID'))
            Items = self.env['sale.order.line'].sudo()
            item_id = Items.search([('production_id', '=', production_id)], limit=1)
            if item_id.sublevel_id.level != 'L4.6':
                raise ValidationError(_("Only Transfer Item With Ready To Pack Level"))
            if item_id:

                item_order_id_fix = item_id.order_id_fix
                actual_total_lines = total_items.filtered(lambda line: line.pair_number > 0)
                if not actual_total_lines:
                    pair_number = 1
                else:
                    nearest_line = actual_total_lines[-1]
                    if nearest_line.order_id_fix == item_order_id_fix:
                        pair_number = nearest_line.pair_number
                    else:
                        pair_number = max(actual_total_lines.mapped('pair_number')) + 1

                self.write({
                    'pair_number': pair_number,
                    'sale_order_line_id': item_id.id,
                })


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
