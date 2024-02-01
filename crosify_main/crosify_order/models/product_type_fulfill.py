from odoo import fields, models

class ProductTypeFulfill(models.Model):
    _name = 'sale.order.product.type.fulfill'
    _description = 'Product Type - Fulfill'
    
    product_type = fields.Many2one('product.template', string='Product Type')
    product_vendor = fields.Many2one('res.partner', string='Product Vendor')
    packing_vendor = fields.Many2one('res.partner', string='Packing Vendor')
    shipping_vendor = fields.Many2one('res.partner', string='Shipping Vendor')