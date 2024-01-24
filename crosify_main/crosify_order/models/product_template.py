# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Type'

    product_type = fields.Char(string="Product Type", compute="compute_product_type", store=True, index=True)
    design_number = fields.Char(string='Design Number', require=True, trim=True)

    # def _create_variant_ids(self):
    #     return

    @api.depends('design_number', 'categ_id')
    def compute_product_type(self):
        for rec in self:
            categ_id = rec.categ_id
            design_number = rec.design_number
            if design_number and categ_id and categ_id.product_category_code:
                rec.product_type = f'{categ_id.product_category_code}{design_number}'
            else:
                rec.product_type = False
    def _prepare_variant_values(self, combination):
        variant_dict = super()._prepare_variant_values(combination)
        sku_suffix = self.env['ir.sequence'].sudo().next_by_code('product.product.sku') or '_Undefined'
        variant_dict['default_code'] = f'{self.product_type}{self.design_number}{sku_suffix}'
        return variant_dict