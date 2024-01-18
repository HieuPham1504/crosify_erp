# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    product_category_code = fields.Char(string='Product Category Code', required=True)