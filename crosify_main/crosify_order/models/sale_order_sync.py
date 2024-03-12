from odoo import api, fields, models

class SaleOrderSync(models.Model):
    _name = 'sale.order.sync'
    _description = 'Sale Order Sync'

    sale_order_id = fields.Many2one('sale.order', string='Order')
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')], string='Status')

