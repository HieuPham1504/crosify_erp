# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_id = fields.Integer(string='Order ID')
    order_id_fix = fields.Integer(string='Order ID Fix')
    crosify_create_date = fields.Datetime(string='Create Date')
    shipping_firstname = fields.Char(string='Shipping First Name')
    shipping_lastname = fields.Char(string='Shipping Last Name')
    shipping_address = fields.Char(string='Shipping Address')
    shipping_city = fields.Char(string='Shipping City')
    shipping_zipcode = fields.Char(string='Shipping Zipcode')
    shipping_country_id = fields.Many2one('res.country', string='Shipping Country')
    shipping_state_id = fields.Many2one('res.country.state', string='Shipping State')
    shipping_phone_number = fields.Char(string='Shipping Phone Number')
    shipping_apartment = fields.Char(string='Shipping Apartment')
    shipping_cost = fields.Float(string='Shipping Cost')
    #payment
    payment_at = fields.Datetime(string='Payment At')
    currency_id = fields.Many2one('res.currency', string='Currency')
    payment_status = fields.Char(string='Payment Status')
    payment_method_id = fields.Many2one('payment.method', string='Payment Method')
    transaction_id = fields.Char(string='Transaction ID')
    discount_code = fields.Char(string='Discount Code')
    channel_ref_id = fields.Char(string='Channel Reference ID')
    logistic_cost = fields.Float(string='Logistic Cost')
    contact_email = fields.Char(string='Contact Email')
    crosify_country_code = fields.Char(string='Country Code', readonly=False)
    state_code = fields.Char(string='State Code')
    #other
    client_secret = fields.Char(string='Client Secret')
    utm_source_id = fields.Many2one('utm.source', string='UTM Source')
    domain = fields.Char(string='Domain')
    tip = fields.Float(string='Tip')
    discount = fields.Float(string='Discount')
    rating = fields.Char(string='Rating')
    review = fields.Text(string='Review')
    extra_info = fields.Text(string='Extra Info')



