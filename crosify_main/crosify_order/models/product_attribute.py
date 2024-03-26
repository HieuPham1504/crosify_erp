# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    code = fields.Char(string='Code')

    _sql_constraints = [
        ('code_unique', 'unique (code)', "The code must be unique."),
    ]

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            name = record.name
            if name:
                duplicate_name = self.sudo().search(
                    [('id', '!=', record.id), ('name', 'ilike', name)])
                if duplicate_name:
                    raise ValidationError(f"This Attribute {name} already exists.")