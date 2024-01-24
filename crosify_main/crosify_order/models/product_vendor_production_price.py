# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductVendorProductionPrice(models.Model):
    _name = "product.vendor.production.price"
    _description = "Vendor Production Price"
    _rec_name = 'partner_id'

    product_id = fields.Many2one('product.product', required=True, index=True, string='SKU')
    partner_id = fields.Many2one(
        'res.partner', 'Vendor',
        ondelete='cascade', required=True,
        check_company=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company.id, index=1)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    price = fields.Float(
        'Price', default=0.0, digits='Production Price',
        required=True)