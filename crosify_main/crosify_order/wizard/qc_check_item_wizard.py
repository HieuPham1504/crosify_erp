# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class QCCheckItemWizard(models.TransientModel):
    _name = 'qc.check.item.wizard'

    qc_pass_line_ids = fields.One2many('qc.check.item.wizard.line', 'check_wizard_id')
    type = fields.Selection([
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='type')

    def action_update_qc_item(self):
        qc_pass_line_ids = self.qc_pass_line_ids
        ItemLevels = self.env['sale.order.line.level'].sudo()
        Orders = self.env['sale.order'].sudo()
        type = self.type
        if type == 'passed':
            qc_passed_level = ItemLevels.search([('level', '=', 'L4.3')], limit=1)
            ready_to_pack_level = ItemLevels.search([('level', '=', 'L4.6')], limit=1)
            if not qc_passed_level:
                raise ValidationError('There is no QC Passed Level')
            for item in qc_pass_line_ids.mapped('sale_order_line_id'):
                order_id_fix = item.order_id_fix
                orders = Orders.search([('order_id_fix', '=', order_id_fix)])
                if len(orders.order_line) == 1:
                    if not ready_to_pack_level:
                        raise ValidationError('There is no Ready To Pack Level')
                    new_level = ready_to_pack_level.id
                else:
                    new_level = qc_passed_level.id
                item.write({
                    'sublevel_id': new_level
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        elif type == 'failed':
            qc_failed_level = ItemLevels.search([('level', '=', 'L4.4')], limit=1)
            if not qc_failed_level:
                raise ValidationError('There is no QC Failed Level')
            if any( not line.error_type_id for line in qc_pass_line_ids):
                raise ValidationError('Error Type Is Required.')
            for line in qc_pass_line_ids:
                item = line.sale_order_line_id
                item.write({
                    'sublevel_id': qc_failed_level.id,
                    'error_type_id': line.error_type_id.id,
                    'error_note': line.note,
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
class QCCheckItemWizardLine(models.TransientModel):
    _name = 'qc.check.item.wizard.line'
    _description = 'QC Check Item Line'

    @api.constrains('sale_order_line_id')
    def _check_sale_order_line_id(self):
        for record in self:
            sale_order_line_id = record.sale_order_line_id
            if sale_order_line_id.sublevel_id.level != 'L4.2':
                raise ValidationError(_("Only Transfer Item With Package Receive Level"))

    check_wizard_id = fields.Many2one('qc.check.item.wizard', string='QC Wizard', required=True, index=True, ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', required=True, string='Item')
    production_id = fields.Char(string='Production ID', required=True, index=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', store=True, index=True)
    product_template_attribute_value_ids = fields.Many2many(
        related='sale_order_line_id.product_template_attribute_value_ids')
    personalize = fields.Char(string='Personalize', related='sale_order_line_id.personalize', store=True)
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', related='sale_order_line_id.sublevel_id', store=True)
    error_type_id = fields.Many2one('fulfill.error', string='Error Type')
    note = fields.Text(string='Note')

    @api.onchange('production_id')
    def onchange_production_id(self):
        production_id = self.production_id
        if production_id:
            duplicate_items = self.check_wizard_id.qc_pass_line_ids.filtered(
                lambda item: item.production_id and item.production_id == production_id)
            if len(duplicate_items) > 1:
                raise ValidationError(_('Duplicate Production ID'))
            Items = self.env['sale.order.line'].sudo()
            item_id = Items.search([('production_id', '=', production_id)], limit=1)
            if item_id.sublevel_id.level != 'L4.2':
                raise ValidationError(_("Only Transfer Item With Package Receive Level"))
            if item_id:
                self.sale_order_line_id = item_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if not val.get('sale_order_line_id'):
                vals_list.remove(val)
        res = super(QCCheckItemWizardLine, self).create(vals_list)
        return res
