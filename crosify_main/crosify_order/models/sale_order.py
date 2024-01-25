# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    myadmin_order_id = fields.Char(string='Order ID')
    order_id_fix = fields.Char(string='Order ID Fix')
    crosify_create_date = fields.Datetime(string='Create Date')
    shipping_firstname = fields.Char(string='Shipping First Name')
    shipping_lastname = fields.Char(string='Shipping Last Name')
    shipping_address = fields.Char(string='Shipping Address')
    shipping_city = fields.Char(string='Shipping City')
    shipping_zipcode = fields.Char(string='Shipping Zipcode')
    shipping_country = fields.Char(string='Shipping Country')
    shipping_state = fields.Char(string='Shipping State')
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
    crosify_country_code_id = fields.Many2one('res.country', string='Country Code')
    state_code_id = fields.Many2one('res.country.state', string='State Code')
    payment_note = fields.Text(string='Payment Note')
    #other
    client_secret = fields.Char(string='Client Secret')
    utm_source_id = fields.Many2one('utm.source', string='UTM Source')
    domain = fields.Char(string='Domain')
    tip = fields.Float(string='Tip')
    discount = fields.Float(string='Discount')
    rating = fields.Char(string='Rating')
    review = fields.Text(string='Review')
    extra_info = fields.Text(string='Extra Info')
    cancel_date = fields.Datetime(string='Cancel Date')
    cancel_reason = fields.Text(string='Cancel Reason')
    tkn = fields.Char(string='TKN')
    tkn_url = fields.Text(string='TKN URL')
    is_upload_tkn = fields.Boolean(string='Is Upload TKN')
    process_tkn_at = fields.Datetime(string='Process TKN Date')
    shipping_carrier_code = fields.Char(string='Shipping Carrier Code')
    base_cost = fields.Float(string='Base Cost')



