# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SelectProductTemplateWizard(models.TransientModel):
    _name = 'select.product.template.wizard'

    product_template_id = fields.Many2one('product.template', string='Product', required=True)
    product_id = fields.Many2one('product.product', required=True)

    def action_set_product_template(self):
        product = self.product_id
        product.product_tmpl_id = self.product_template_id.id
