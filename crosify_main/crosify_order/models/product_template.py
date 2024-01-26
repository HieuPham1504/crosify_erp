# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Type'

    product_type = fields.Char(string="Product Type", compute="compute_product_type", store=True, index=True)
    design_number = fields.Char(string='Design Number', require=True, trim=True)
    detailed_type = fields.Selection(string="Detailed Type")

    # def _create_variant_ids(self):
    #     return

    def create_variants(self):
        self._create_variant_ids()

    @api.constrains('product_type')
    def _check_product_type(self):
        for record in self:
            product_type = record.product_type

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('product_type', '=', product_type)])
            if duplicate_code:
                raise ValidationError(_("This Product Type already exists."))


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
        return