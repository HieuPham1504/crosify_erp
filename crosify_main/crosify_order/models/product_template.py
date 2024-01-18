# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_type = fields.Char(string="Product Type")
    default_code = fields.Char(string='Product Code')

    def _create_variant_ids(self):
        return