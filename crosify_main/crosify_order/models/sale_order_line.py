# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    image_ids = fields.Many2many('ir.attachment', string='Images')
    crosify_created_date = fields.Date(string='Create Date')
    product_sku = fields.Char(string='SKU', related='product_id.default_code', store=True, index=True)
    my_admin_order_id = fields.Char(string='My Admin Order ID', store=True, index=True)
    order_id_fix = fields.Char(string='Order ID Fix', store=True, index=True)
    product_name = fields.Char(string='Product Name', related='product_id.name', store=1)
    product_vendor_id = fields.Many2one('res.partner', string='Product Vendor')
    item_size = fields.Char(string='Item Size')
    description_item_size = fields.Char(string='Description Item Size')
    color_item = fields.Char(string='Color Item')
    box_size = fields.Char(string='Box Size')
    personalize = fields.Char(string='Personalize')
    package_size = fields.Char(string='Package Size')
    product_code = fields.Char(string='Product Code')
    product_type = fields.Char(string='Product Type')
    color_set_name = fields.Char(string='Color Set Name')
    design_serial_number = fields.Char(string='Design Serial Number')
    accessory_name = fields.Char(string='Accessory Name')
    base_cost = fields.Float(string='Base Cost')
    shipping_cost = fields.Float(string='Shipping Cost')
    logistic_cost = fields.Float(string='Logistic Cost')
    customer_note = fields.Text(string='Customer Note')
    priority = fields.Boolean(string='Priority')
    element_message = fields.Text(string='Element Message')
    extra_info = fields.Text(string='Extra Info')
    extra_service = fields.Char(string='Extra Service')
    status = fields.Char(string='Status')
    tips = fields.Float(string='Tips')
    #Fulfillment
    operator_id = fields.Many2one('hr.employee', string='Operator')
    produce_vendor_id = fields.Many2one('res.partner', string='Produce Vendor')
    hs_code = fields.Char(string='HS Code')
    tkn_code = fields.Char(string='TKN Code')
    tkn_url = fields.Char(string='TKN URL')
    label_file = fields.Binary(string='Label File')
    upload_tkn_date = fields.Datetime(string='Upload TKN Date')
    upload_tkn_by = fields.Many2one('hr.employee', string='Upload TKN By')
    is_upload_tkn = fields.Boolean(string='Is Upload TKN')
    fulfill_date = fields.Date(string='Fulfill Date')
    note_fulfill = fields.Text(string='Note Fulfill')

    #Design
    designer_id = fields.Many2one('hr.employee', string='Designer')
    design_file = fields.Binary(string='Design File')
    design_date = fields.Date(string='Design Date')
    variant = fields.Text(string='Variant')
    #tab production
    production_id = fields.Char(string='Production Id')
    production_vendor_code = fields.Char(string='Production Vendor Code')
    production_vendor_id = fields.Many2one('res.partner', string='Production Vendor')
    packaging_location = fields.Char(string='Packaging Location')
    package_status = fields.Char(string='Package Status')
    shipping_method = fields.Char(string='Shipping Method')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')
    production_date = fields.Date(string='Production Date')
    production_status = fields.Char(string='Production Status')
    production_estimate_time = fields.Datetime(string='Production Estimate Time')
    production_note = fields.Text(string='Production Note')
    #Tab Shipping & Pickup
    address_sheft = fields.Char(string='Address Sheft')
    shipping_date = fields.Datetime(string='Shipping Date')
    shipping_confirm_date = fields.Datetime(string='Shipping Confirm Date')
    packed_date = fields.Datetime(string='Packed Date')
    pickup_date = fields.Date(string='Pickup Date')
    deliver_date = fields.Date(string='Deliver Date')
    deliver_status = fields.Char(string='Deliver Status')
    customer_received = fields.Boolean(string='Customer Received')
    #Tab Other Info
    note_change_request = fields.Text(string='Note Change Request')
    cancel_date = fields.Date(string='Cancel Date')
    cancel_reason = fields.Date(string='Cancel Reason')
    cancel_status = fields.Char(string='Cancel Status')
    dispute_status = fields.Char(string='Dispute Status')
    dispute_note = fields.Text(string='Dispute Note')
    approve_by = fields.Many2one('hr.employee', string='Approve By')

    level = fields.Many2one('sale.order.line.level', domain=[('is_parent', '=', True)])
    sublevel = fields.Many2one('sale.order.line.level', domain=[('is_parent', '=', False)])
    meta_field = fields.Text(string='Meta Field')
    crosify_discount_amount = fields.Float(string='Discount Amount')
    total_tax = fields.Float(string='Total Tax')




