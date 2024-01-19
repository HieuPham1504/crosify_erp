# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char(string='SKU')

    def action_select_product_template(self):
        return {
            'name': 'Select Product',
            'view_mode': 'form',
            'res_model': 'select.product.template.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_id': self.id}
        }