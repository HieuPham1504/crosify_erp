# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class UpdateFulFillmentWizard(models.TransientModel):
    _name = 'update.fulfillment.wizard'

    update_type = fields.Selection([
        ('default', "Update Vendor Fulfillment By System Config"),
        ('specific_user', "Update Vendor Fulfillment For Specific User")
    ], default='default', required=True)
    production_vendor_id = fields.Many2one('res.partner', string='Product Vendor')
    packaging_vendor_id = fields.Many2one('res.partner', string='Packaging Vendor')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')

    def action_update_fulfill(self):
        item_ids = self._context.get('active_ids', [])
        items = self.env['sale.order.line'].sudo().search([('id', 'in', item_ids)], order='id asc')
        employee_id = self.env.user.employee_id.id
        update_type = self.update_type
        fulfilled_vendor_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.0')], limit=1)
        if not fulfilled_vendor_level:
            raise ValidationError('There is no status Fulfill Vendor')

        for item in items:
            item.with_delay(
                description=f'Action Update Fulfillment Vendor For Item With Production ID = {item.production_id}',
                channel='root.channel_sale_order_line').action_cron_action_update_fulfill_vendor(update_type, employee_id, fulfilled_vendor_level)
