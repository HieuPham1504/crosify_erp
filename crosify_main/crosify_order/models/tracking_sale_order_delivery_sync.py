from odoo import api, fields, models

class TrackingSaleOrderDeliverySync(models.Model):
    _name = 'tracking.sale.order.delivery.sync'
    _description = 'Tracking Sale Order Delivery Sync'
    _order = 'create_date desc'

    sale_order_id = fields.Many2one('sale.order', string='Order')
    description = fields.Text(string='Description')
    description_json = fields.Json(string='Description JSON')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')], string='Status')
    response = fields.Text(string='Response')

    remote_ip_address = fields.Char(string='Remote IP Address')

