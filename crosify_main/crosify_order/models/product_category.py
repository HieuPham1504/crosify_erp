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

            if name:
                duplicate_name = self.sudo().search(
                    [('id', '!=', record.id), ('name_lower', '=', name.lower())])
                if duplicate_name:
                    raise ValidationError(_("This Product Category Name already exists."))
            if product_category_code:
                duplicate_code = self.sudo().search([('id', '!=', record.id), ('product_category_code_lower', '=', product_category_code.lower())])
                if duplicate_code:
                    raise ValidationError(_("This Product Category Code already exists."))


    name = fields.Char(trim=True)
    name_lower = fields.Char(compute='compute_name_lower', trim=True, store=True)
    product_category_code = fields.Char(string='Product Category Code', required=True, trim=True)
    product_category_code_lower = fields.Char(compute='compute_product_code_lower', trim=True, store=True)

    @api.depends('name')
    def compute_name_lower(self):
        for rec in self:
            rec.name_lower = rec.name.lower() if rec.name else False

    @api.depends('name')
    def compute_product_code_lower(self):
        for rec in self:
            rec.product_category_code_lower = rec.product_category_code.lower() if rec.product_category_code else False