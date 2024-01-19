# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_type = fields.Char(string="Product Type")
    default_code = fields.Char(string='Product Code')

    # def _create_variant_ids(self):
    #     return

    def _prepare_variant_values(self, combination):
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict['default_code'] = f'{self.product_type}{self.default_code}'
        return variant_dict