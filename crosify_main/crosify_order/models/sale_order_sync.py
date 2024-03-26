from odoo import api, fields, models

class SaleOrderSync(models.Model):
    _name = 'sale.order.sync'
    _description = 'Sale Order Sync'
    _order = 'create_date desc'

    sale_order_id = fields.Many2one('sale.order', string='Order')
    description = fields.Text(string='Description')
    description_json = fields.Json(string='Description JSON')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')], string='Status')
    response = fields.Text(string='Response')

    type = fields.Selection([
        ('create', 'Create'),
        ('update', 'Update')], string='Type')
    remote_ip_address = fields.Char(string='Remote IP Address')

