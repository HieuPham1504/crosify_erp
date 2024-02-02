from odoo import api, fields, models

class ProductTypeFulfill(models.Model):
    _name = 'sale.order.product.type.fulfill'
    _description = 'Product Type - Fulfill'
    
    product_type_id = fields.Many2one('product.template', string='Product Type')
    product_vendor_id = fields.Many2one('res.partner', string='Product Vendor')
    packaging_vendor_id = fields.Many2one('res.partner', string='Packaging Vendor')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')
    