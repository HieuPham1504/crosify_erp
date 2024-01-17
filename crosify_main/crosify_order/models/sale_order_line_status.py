# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    code = fields.Char(string='Code', required=True, index=True)
    name = fields.Char(string='Name', required=True)
    color = fields.Integer('Color', default=0)
    is_active = fields.Boolean(string='Active', default=True)
