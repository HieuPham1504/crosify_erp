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
        for item in items:
            data = item.get_label_json_data()
            item.with_delay(description=data).action_creating_shipment_for_order()

    def action_creating_shipment_for_order(self):
        for rec in self:
            rec.generate_order_label_file()
            can_update_tkn_items = rec.order_line.filtered(lambda item: not item.is_upload_tkn)
            can_update_tkn_items.action_creating_shipment_for_item_order()

    def get_label_json_data(self):
        parcel_datas = []
        HSCodeConfigs = self.env['hs.product.config'].sudo()
        States = self.env['res.country.state'].sudo()
        Items = self.env['sale.order.line'].sudo()
        customer = self.partner_id
        items = Items
        total_item = self.order_line
        total_weight = sum(total_item.product_id.mapped('weight'))

        item_hs_codes = total_item.mapped('hs_code')
        for hs_code in item_hs_codes:
            first_item = total_item.filtered(lambda item: item.hs_code == hs_code)[0]
            items |= first_item

        weight_param = round(60 * total_weight / 100000, 3)
        length_param = min(items.mapped('length'))
        height_param = min(items.mapped('height'))
        width_param = min(items.mapped('width'))

        for item in items:
            hs_code = item.hs_code
            hs_code_product_config = HSCodeConfigs.search([('hs_code', '=', hs_code)], limit=1)
            if not hs_code_product_config:
                raise ValueError(f"There is no Config with HS Code {hs_code}")
            parcel_datas.append({
                "EName": f"{hs_code_product_config.product_ename}",
                "CName": f"{hs_code_product_config.product_cname}",
                "HTSCode": f"{hs_code}",
                "DGCode": "",
                "Coo": "US",
                "Quantity": 1,
                "UnitPrice": item.price_unit,
                "UnitWeight": item.product_id.weight,
                "UnitLength": item.product_id.length,
                "UnitHeight": item.product_id.height,
                "UnitWidth": item.product_id.width,
                "SKU": f"{item.product_id.default_code}",
                "Url": f"{item.design_file_url if item.design_file_url else ''}"
            })

        json_data = {
            "ReferenceNumber": f"{self.order_id_fix}",
            "Weight": weight_param,
            "Length": length_param,
            "Height": height_param,
            "Width": width_param,
            "Service": "HPW Parcel",
            "ServiceCode": "HPW_PB_LAX",
            "CurrencyCode": f"{self.currency_id.name}",
            "Override": False,
            "Consignor": {
                "CountryCode": "CN",
                "Name": "xin",
                "Company": "test gs",
                "Street": "3/F,Second Phase,Qianlong Logistics Park,,China South City,Pinghu,Longgang",
                "Street2": "1",
                "City": "SHEN ZHEN",
                "State": "GUANG DONG",
                "Zip": "518111",
                "Phone": "17727165012"
            },
            "Receiver": {
                "CountryCode": f"{customer.country_id.code}",
                "Name": f"{customer.name}",
                "Company": f"{customer.company_id.name if customer.company_id else ''}",
                "Street": f"{customer.street}",
                "Street2": f"{customer.street2}",
                "City": f"{customer.city}",
                "State": f"{customer.state_id.code}",
                "Zip": f"{customer.zip}",
                "Phone": f"{customer.phone}",
                "Email": f"{customer.email}",
                "Province": "TX"
            },
            "Parcels": parcel_datas
        }
        return json_data
    def get_label_data(self):
        client_key = self.env['ir.config_parameter'].sudo().get_param('create.label.client.key')
        if not client_key:
            raise ValueError("Not Found Client Key")


        headers = {"Content-Type": "application/json", "Accept": "application/json", "Catch-Control": "no-cache",
                   "clientkey": f"{client_key}"}
        customer = self.partner_id
        if customer.country_id.code != 'US':
            service_type = 3
        else:
            service_type = customer.state_id.service_type
        url = f"https://myadmin.crosify.com/api/labels/{service_type}"
        json_data = self.get_label_json_data()

        return requests.post(url, data=json.dumps(json_data), headers=headers)

    def generate_order_label_file(self):
        response = self.get_label_data()
        if response.status_code == 200:
            total_data = json.loads(response.text)
            data = total_data.get('labels')[0]
            current_employee = self.env.user.employee_id
            now = fields.Datetime.now()
            self.write({
                'label_file_url': data.get('linkPdf'),
                'tkn': data.get('trackingNumber'),
                'is_upload_tkn': True,
                'update_tkn_date': now,
                'update_tkn_employee_id': current_employee.id,
            })
        else:
            raise ValidationError(response.reason)
        return True

    @api.model
    def action_merge_order(self):
        order_ids = self._context.get('active_ids', [])
        orders = self.sudo().search([('id', 'in', order_ids)], order='id asc')
        new_order_id_fix = False
        order_id_fixes = orders.mapped('order_id_fix')
        if len(order_id_fixes) == 0:
            raise ValidationError('Can Not Merge None Order ID Fix Orders')
        else:
            new_order_id_fix = order_id_fixes[0]
        for order in orders:
            order.order_id_fix = new_order_id_fix
