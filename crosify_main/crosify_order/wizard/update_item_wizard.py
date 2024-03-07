
# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pytz


class UpdateItemWizard(models.TransientModel):
    _name = 'update.item.wizard'

    line_ids = fields.One2many('update.item.line.wizard', 'update_item_wizard_id', string='Update Items')


class UpdateItemWizard(models.TransientModel):
    _name = 'update.item.wizard'

    update_item_wizard_id = fields.Many2one('update.item.wizard')
    production_id = fields.Char(string='Production ID', required=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item')
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id')
