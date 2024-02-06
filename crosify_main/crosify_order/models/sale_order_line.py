# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def default_sublevel_id(self):
        payment_status = self.order_id.payment_status
        level_code = 'L1.1' if payment_status else 'L1'
        level = self.env['sale.order.line.level'].sudo().search([('level', '=', level_code)], limit=1)
        return level.id

    image_ids = fields.Many2many('ir.attachment', string='Images')
    crosify_created_date = fields.Date(string='Create Date')
    crosify_create_by = fields.Char(string='Created By')
    product_sku = fields.Char(string='SKU', related='product_id.default_code', store=True, index=True)
    my_admin_order_id = fields.Char(string='My Admin Order ID', store=True, index=True)
    my_admin_detailed_id = fields.Integer(string='My Admin Detailed ID', store=True, index=True)
    myadmin_product_id = fields.Integer(string='My Admin Product ID')
    order_id_fix = fields.Char(string='Order ID Fix', related='order_id.order_id_fix', store=True, index=True)
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
    channel_ref_id = fields.Char(string='Reference ID')
    #Fulfillment
    operator_id = fields.Many2one('hr.employee', string='Operator')
    produce_vendor_id = fields.Many2one('res.partner', string='Produce Vendor')
    hs_code = fields.Char(string='HS Code')
    tkn_code = fields.Char(string='TKN Code')
    tkn_url = fields.Char(string='TKN URL')
    label_file = fields.Binary(string='Label File')
    label_file_store_name = fields.Char(string='Label File Store Name')
    upload_tkn_date = fields.Datetime(string='Upload TKN Date')
    upload_tkn_by = fields.Many2one('hr.employee', string='Upload TKN By')
    is_upload_tkn = fields.Boolean(string='Is Upload TKN')
    fulfill_date = fields.Date(string='Fulfill Date')
    note_fulfill = fields.Text(string='Fulfill Note')

    #Design
    designer_id = fields.Many2one('hr.employee', string='Designer')
    design_file_url = fields.Text(string='Design File')
    design_file_name = fields.Text(string='Design File Name')
    design_date = fields.Date(string='Design Date')
    variant = fields.Text(string='Variant')
    #tab production
    production_id = fields.Char(string='Production ID')
    production_vendor_code = fields.Char(string='Production Vendor Code')
    production_vendor_id = fields.Many2one('res.partner', string='Production Vendor')
    packaging_location = fields.Char(string='Packaging Location')
    package_status = fields.Char(string='Package Status')
    packaging_vendor_id = fields.Many2one('res.partner', string='Packaging Vendor')
    shipping_method = fields.Char(string='Shipping Method')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')
    production_start_date = fields.Date(string='Production Start Date')
    production_done_date = fields.Date(string='Production Done Date')
    production_status = fields.Char(string='Production Status')
    production_estimate_time = fields.Integer(string='Production Estimate Time (h)')
    production_note = fields.Text(string='Production Note')
    #Tab Shipping & Pickup
    address_sheft = fields.Char(string='Address Sheft')
    shipping_date = fields.Datetime(string='Shipping Date')
    shipping_confirm_date = fields.Date(string='Shipping Confirm Date')
    packed_date = fields.Datetime(string='Packed Date')
    pickup_date = fields.Datetime(string='Pickup Date')
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

    level_id = fields.Many2one('sale.order.line.level', domain=[('is_parent', '=', True)], string='Parent Level')
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', default=default_sublevel_id)
    last_update_level_date = fields.Datetime(string='Last Update Level')
    meta_field = fields.Text(string='Meta Field')
    crosify_discount_amount = fields.Float(string='Discount Amount')
    total_tax = fields.Float(string='Total Tax')
    cost_amount = fields.Float(string='Cost Amount')
    amount = fields.Float(string='Amount')
    variant = fields.Text(string='Variant')
    taxed_total_amount = fields.Float(string='Taxed Total Amount')
    crosify_approve_cancel_employee_id = fields.Many2one('hr.employee', string='Approve Cancel By')
    update_date = fields.Datetime(string='Update Date')
    update_by = fields.Char(string='Update By')
    chars = fields.Char(string='Chars')











