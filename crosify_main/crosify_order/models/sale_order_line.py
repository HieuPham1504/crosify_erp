# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_vendor_id = fields.Many2one('res.partner', string='Product Vendor')
    