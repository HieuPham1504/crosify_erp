# -*- coding: utf-8 -*-
import json
import requests
import random
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _sql_constraints = [
        ('myadmin_order_id_uniq', 'unique (myadmin_order_id)',
         "The Order ID must be unique, this one is already assigned to another sale order."),
    ]

    myadmin_order_id = fields.Char(string='Order ID', required=True)
    order_id_fix = fields.Char(string='Order ID Fix', tracking=1, required=True, index=1)
    crosify_create_date = fields.Datetime(string='Create Date', default=fields.datetime.today(), required=True)
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
    label_file_attachment = fields.Binary(string="Label File")
    label_file_store_name = fields.Char(string="File Name")
    label_file_url = fields.Text(string="Label File Url")
    # payment
    payment_at = fields.Datetime(string='Payment Date')
    currency_id = fields.Many2one('res.currency', string='Currency')
    payment_status = fields.Boolean(string='Payment Status', tracking=1)
    payment_method_id = fields.Many2one('payment.method', string='Payment Method')
    transaction_id = fields.Char(string='Transaction ID')
    discount_code = fields.Char(string='Discount Code')
    channel_ref_id = fields.Char(string='Channel Reference ID')
    logistic_cost = fields.Float(string='Logistic Cost')
    contact_email = fields.Char(string='Contact Email')
    crosify_country_code_id = fields.Many2one('res.country', string='Country Code')
    state_code_id = fields.Many2one('res.country.state', string='State Code')
    payment_note = fields.Text(string='Payment Note')
    # other
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
    tkn = fields.Char(string='TKN Code')
    tkn_url = fields.Text(string='TKN URL')
    update_tkn_date = fields.Datetime(string='Update TKN Date')
    update_tkn_employee_id = fields.Many2one('hr.employee', string='Update TKN By')
    is_upload_tkn = fields.Boolean(string='Is Upload TKN')
    tracking_note = fields.Text(string='Note')
    process_tkn_at = fields.Datetime(string='Process TKN Date')
    shipping_carrier_code = fields.Char(string='Shipping Carrier Code')
    base_cost = fields.Float(string='Base Cost')
    crosify_create_by = fields.Char(string='Create By')
    crosify_updated_by = fields.Char(string='Updated By')
    started_checkout_code = fields.Char(string='Started Checkout Code')
    crosify_update_date = fields.Datetime(string='Update Date')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')
    order_payment_state = fields.Selection([
        ('paid', "Paid"),
        ('not_paid', "Not Paid")
    ], default='not_paid', compute='compute_order_payment_state', store=True, index=True)
    order_type_id = fields.Many2one('sale.order.type', string='Order Type', required=True, index=True)
    state = fields.Selection(default='sale')

    @api.depends('payment_status')
    def compute_order_payment_state(self):
        for rec in self:
            rec.order_payment_state = 'paid' if rec.payment_status else 'not_paid'

    @api.onchange('payment_status')
    def onchange_order_payment_status(self):
        payment_status = self.payment_status
        level_code = 'L1.1' if payment_status else 'L1'
        level = self.env['sale.order.line.level'].sudo().search([('level', '=', level_code)], limit=1)
        items = self.order_line
        for item in items:
            item_sublevel = item.sublevel_id
            if not item_sublevel or item_sublevel.level.strip() == 'L1' or item_sublevel.level.strip() == 'L1.1':
                item.sublevel_id = level.id

    @api.model
    def action_creating_shipment_for_order_model(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        items.action_creating_shipment_for_order()

    def action_creating_shipment_for_order(self):
        current_employee = self.env.user.employee_id
        now = fields.Datetime.now()
        for rec in self:
            rec.write({
                'is_upload_tkn': True,
                'update_tkn_date': now,
                'update_tkn_employee_id': current_employee.id,
            })
            can_update_tkn_items = rec.order_line.filtered(lambda item: not item.is_upload_tkn)
            can_update_tkn_items.action_creating_shipment_for_item()

    def generate_order_label_file(self):
        client_key = self.env['ir.config_parameter'].sudo().get_param('create.label.client.key')
        if not client_key:
            raise ValueError("Not Found Client Key")
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache", "clientkey": f"{client_key}"}
        index = random.randrange(10000000, 90000000)
        url = "https://myadmin.crosify.com/api/labels"
        json_data = {
            "ReferenceNumber": f"TESTREFERENCENUMBE92847{index}",
            "X-HPW-Service-Type": 1,
            "Weight": 0.545,
            "Receiver": {
                "CountryCode": "US",
                "Name": "Test",
                "Company": "gs",
                "Street": "67700 test Lockwood-Jolon Road",
                "Street2": "1",
                "City": "Lockwood",
                "State": "California",
                "Zip": "93932",
                "Phone": "5869098233",
                "Email": " 12345@email.com "
            },
            "Parcels": [
                {
                    "EName": "shirt",
                    "CName": "衬衫",
                    "HSCode": 12345678,
                    "Quantity": 1,
                    "UnitPrice": 30,
                    "UnitWeight": 0.45,
                    "SKU": "SKU1",
                    "CurrencyCode": "USD"
                }

            ]
        }

        response = requests.post(url, data=json.dumps(json_data), headers=headers)
        data = json.loads(response.text)
        if response.status_code == 200:
            self.write({
                'label_file_url': data.get('linkPdf'),
                'tkn': data.get('shipmentId'),
            })
        else:
            raise ValidationError(data.get('msg'))
        return True
