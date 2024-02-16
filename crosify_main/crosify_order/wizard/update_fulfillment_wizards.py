# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class UpdateFulFillmentWizard(models.TransientModel):
    _name = 'update.fulfillment.wizard'

    update_type = fields.Selection([
        ('default', "Update Fulfillment By System Config"),
        ('specific_user', "Update Fulfillment For Specific User")
    ], default='default', required=True)
    update_user_ids = fields.Many2many('update.fulfillment.user.config', string='Update User')
    production_vendor_id = fields.Many2one('res.partner', string='Product Vendor')
    packaging_vendor_id = fields.Many2one('res.partner', string='Packaging Vendor')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')

    def action_update_fulfill(self):
        item_ids = self._context.get('active_ids', [])
        items = self.env['sale.order.line'].sudo().search([('id', 'in', item_ids)], order='id asc')
        employee_id = self.env.user.employee_id.id
        update_type = self.update_type
        update_user_ids = self.update_user_ids
        for item in items:
            product_type_fulfill_data = self.env['sale.order.product.type.fulfill'].sudo().search(
                [('product_type_id', '=', item.product_id.product_tmpl_id.id)], limit=1)
            if product_type_fulfill_data:
                fulfilled_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L2.2')], limit=1)
                if not fulfilled_level:
                    raise ValidationError('There is no status Fulfilled')
                item_fields_mapping = {
                    'production_vendor_id': 'product_vendor_id',
                    'packaging_vendor_id': 'packaging_vendor_id',
                    'shipping_vendor_id': 'shipping_vendor_id',
                }
                for field in item_fields_mapping:
                    if update_type == 'default':
                        item[field] = product_type_fulfill_data[item_fields_mapping[field]].id
                    else:
                        item[field] = self[field].id


                item.fulfill_employee_id = employee_id
                item.fulfill_date = datetime.now().date()
                item.sublevel_id = fulfilled_level.id
