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
        item_fields_mapping = {
            'production_vendor_id': 'product_vendor_id',
            'packaging_vendor_id': 'packaging_vendor_id',
            'shipping_vendor_id': 'shipping_vendor_id',
        }
        for item in items:
            if update_type == 'default':
                product_type_fulfill_data = self.env['sale.order.product.type.fulfill'].sudo().search(
                    [('product_type_id', '=', item.product_id.product_tmpl_id.id)], limit=1)
                if product_type_fulfill_data:
                    for field in item_fields_mapping:
                        item[field] = product_type_fulfill_data[item_fields_mapping[field]].id
            else:
                for field in item_fields_mapping:
                    item[field] = self[field].id

            item.write({
                'fulfill_vendor_employee_id': employee_id,
                'fulfill_vendor_date': datetime.now(),
                'sublevel_id': fulfilled_vendor_level.id,
            })
