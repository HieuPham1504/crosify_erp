# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.constrains('name', 'product_category_code')
    def _check_description(self):
        for record in self:
            name = record.name
            product_category_code = record.product_category_code

            duplicate_name = self.sudo().search(
                [('id', '!=', record.id), ('name', '=', name)])
            if duplicate_name:
                raise ValidationError(_("This Product Category Name already exists."))

            duplicate_code = self.sudo().search([('id', '!=', record.id), ('product_category_code', '=', product_category_code)])
            if duplicate_code:
                raise ValidationError(_("This Product Category Code already exists."))


    name = fields.Char(trim=True)
    product_category_code = fields.Char(string='Product Category Code', required=True, trim=True)