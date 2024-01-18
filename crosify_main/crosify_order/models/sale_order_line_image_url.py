# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLineImageUrl(models.Model):
    _name = 'sale.order.line.image.url'

    image_url = fields.Text(string='Image URL', required=True)
    order_line_id = fields.Many2one('sale.order.line')