# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import http
import requests
from odoo.http import Controller, request, Response, route

import hmac
import hashlib
import base64

ORDER_FIELDS_MAPPING = {
    'order_id': 'myadmin_order_id',
    'name': 'name',
    'Transactionid': 'transaction_id',
    'ChannelREfID': 'channel_ref_id',
    'ShippingFirstname': 'shipping_firstname',
    'ShippingLastname': 'shipping_lastname',
    'ShippingAddress': 'shipping_address',
    'ShippingCity': 'shipping_city',
    'ShippingZipcode': 'shipping_zipcode',
    'ShippingPhonenumber': 'shipping_phone_number',
    'ShippingApartment': 'shipping_apartment',
    'ContactEmail': 'contact_email',
    'CustomerNote': 'note',
    'ClientSecret': 'client_secret',
    'Domain': 'domain',
    'Tip': 'tip',
    'ShippingCost': 'shipping_cost',
    'Subtotal': 'untaxed_amount',
    'Discount': 'discount',
    'TotalAmount': 'amount_total',
    'Paymentat': 'payment_at',
    'PaymentStatus': 'payment_status',
    'PaymentNote': 'payment_note',
    'PaymentNote': 'payment_note',
    'DiscountCode': 'discount_code',
    'LogisticCost': 'logistic_cost',
    'Rating': 'rating',
    'Review': 'review',
    'Updatedat': 'crosify_update_date',
    'UpdatedBy': 'crosify_updated_by',
    'Createdat': 'crosify_create_date',
    'Tkn': 'tkn',
    'IsUploadTKN': 'is_upload_tkn',
    'TrackingUrl': 'tkn_url',

}

ORDER_LINE_FIELDS_MAPPING = {
    'Detailid': 'my_admin_detailed_id',
    'Orderid': 'my_admin_order_id',
    'OrderidFix': 'order_id_fix',
    'ProductID': 'production_id',
    'Metafield': 'meta_field',
    'CustomerNote': 'customer_note',
    'Personalize': 'personalize',
    'ElementMessage': 'element_message',
    'DesignFile': 'design_file',
    'DesignDate': 'design_date',
    'DesignDate': 'design_date',
    'ExtraService': 'extra_service',
    'FulfillNote': 'note_fulfill',
    'FulfillDate': 'fulfill_date',
    'ProductionDate': 'production_date',
    'ProductionStatus': 'production_status',
    'ProductionEstimatedTime': 'production_estimate_time',
    'ProductionNote': 'production_note',
    'ShippingDate': 'shipping_date',
    'ShippingConfirmDate': 'shipping_confirm_date',
    'ShippingConfirmDate': 'shipping_confirm_date',
    'ShippingMethod': 'shipping_method',
    'PackagingLocation': 'packaging_location',
    'Priority': 'packed_date',
    'PickupDate': 'pickup_date',
    'DeliveryStatus': 'deliver_status',
    'DeliveryUpdateDate': 'deliver_date',
    'DescriptionItemSize': 'description_item_size',
    'Boxsize': 'box_size',
    'Packagesize': 'package_size',
    'DesignSerialno': 'design_serial_number',
    'ColorsetName': 'color_set_name',
    'AccessoryName': 'accessory_name',
    'ColorItem': 'color_item',
    'HScode': 'HScode',
    'LabelFile': 'label_file',
    'TKN': 'tkn_code',
    'UploadTknat': 'upload_tkn_date',
    'TrackingUrl': 'tkn_url',
    'IsUploadTKN': 'is_upload_tkn',
    'ChangeRequestNote': 'note_change_request',
    'DisputeStatus': 'dispute_status',
    'DisputeNote': 'dispute_note',
    'Canceledat': 'cancel_date',
    'CancelReason': 'cancel_reason',
    'CancelStatus': 'cancel_status',
    'Updatedat': 'update_date',
    'Createdat': 'crosify_created_date',
    'LastupdateLevel': 'last_update_level_date',
    'PackagingLocationInfo': 'packaging_location',
    'PackagingLocationInfo': 'packaging_location',
}


class SaleOrderController(Controller):

    def verify_webhook(self, data, hmac_header):
        CLIENT_SECRET = request.env['ir.config_parameter'].sudo().get_param('hmac_sha256_secret', False)
        digest = hmac.new(CLIENT_SECRET.encode('utf-8'), data, digestmod=hashlib.sha256).digest()
        computed_hmac = base64.b64encode(digest)

        return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

    @route("/api/sale_orders", methods=["POST"], type="json", auth="public", cors="*")
    def action_create_sale_order(self, **kwargs):
        data = request.get_json_data()
        # verified = self.verify_webhook(data, request.httprequest.headers['X-Crosify-Hmac-SHA256'])
        verified = True
        if not verified:
            return Response("Bad Request", status=400)
        else:

            shipping_state_sql = f"""
            select id 
                    from res_country_state 
                    where code = '{data.get('StateCode')}' 
                    limit 1
            """

            request.env.cr.execute(shipping_state_sql)
            shipping_state_id = request.env.cr.fetchone()[0]

            shipping_country_sql = f"""
            select id 
                    from res_country
                    where code = '{data.get('CountryCode')}'
                    limit 1
            
            """

            request.env.cr.execute(shipping_country_sql)
            shipping_country_id = request.env.cr.fetchone()[0]

            partner_sql = f"""
            insert into res_partner(name,street,street2,city,state_id,zip,country_id,phone,mobile,email) 
            values (
            '{data.get('ShippingFirstname', '')} {data.get('ShippingLastname', '')}', 
            '{data.get('ShippingAddress', '')}',
            '{data.get('ShippingApartment', '')}',
            '{data.get('ShippingCity', '')}',
            {shipping_state_id},
            '{data.get('ShippingZipcode', '')}',
            {shipping_country_id},
            '{data.get('ShippingPhonenumber', '')}',
            '{data.get('ShippingPhonenumber', '')}',
            '{data.get('ContactEmail', '')}'
            ) 
            returning id
            """

            request.env.cr.execute(partner_sql)
            partner_id = request.env.cr.fetchone()[0]


            create_order_sql = f"""
                with currency as (
                    select id 
                    from res_currency 
                    where name = '{data.get('Currency')}' 
                    limit 1
                ), 

                order_create_employee as (
                    select id
                    from hr_employee 
                    where work_email = '{data.get('CreatedBy')}' 
                    limit 1 
                ),
                order_update_employee as (
                    select id
                    from hr_employee 
                    where work_email = '{data.get('UpdatedBy')}' 
                    limit 1
                )

                insert into sale_order(
                name,
                myadmin_order_id,
                transaction_id,
                channel_ref_id,
                shipping_firstname,
                shipping_lastname,
                shipping_address,
                shipping_city,
                shipping_zipcode,
                shipping_country_id,
                shipping_state_id,
                shipping_phone_number,
                shipping_apartment,
                contact_email,
                note,
                client_secret,
                domain,
                tip,
                shipping_cost,
                amount_untaxed,
                discount,
                amount_total,
                payment_at,
                currency_id,
                payment_status,
                payment_note,
                discount_code,
                logistic_cost,
                rating,
                review,
                crosify_update_date,
                crosify_updated_by,
                crosify_create_date,
                crosify_create_by,
                tkn,
                is_upload_tkn,
                tkn_url, 
                company_id,
                partner_id
                ) 
                Select '{data.get('Name', '')}', '{data.get('Orderid', '')}', '{data.get('Transactionid', '')}', '{data.get('ChannelRefID', '')}', '{data.get('ShippingFirstname', '')}',
                       '{data.get('ShippingLastname', '')}', '{data.get('ShippingAddress', '')}', '{data.get('ShippingCity', '')}', '{data.get('shipping_zipcode', '')}', 
                       {shipping_country_id}, {shipping_state_id}, 
                       '{data.get('ShippingPhonenumber', '')}', '{data.get('ShippingApartment', '')}', '{data.get('ContactEmail', '')}', '{data.get('CustomerNote', '')}',
                       '{data.get('ClientSecret', '')}', '{data.get('Domain', '')}', {data.get('Tip', False)}, {data.get('ShippingCost', False)}, {data.get('Subtotal', False)},
                       {data.get('Discount')}, {data.get('TotalAmount')}, '{data.get('Paymentat')}',  (select currency.id from currency), 
                       '{data.get('PaymentStatus', '')}', '{data.get('PaymentNote', '')}', '{data.get('DiscountCode', '')}',  
                       """
            if data.get('LogisticCost'):
                create_order_sql += f"""
                           '{data.get('LogisticCost', False)}', """
            else:
                create_order_sql += "0,"
            create_order_sql += f"""
                       '{data.get('rating', '')}', '{data.get('review', '')}', '{data.get('Updatedat')}', (select order_update_employee.id from order_update_employee),
                       '{data.get('Createdat')}', (select order_create_employee.id from order_create_employee), '{data.get('Tkn', '')}', {data.get('IsUploadTKN', )}, 
                       '{data.get('TrackingUrl', '')}', {request.env(su=True).company.id}, {partner_id}
             Returning id
            """
            request.env.cr.execute(create_order_sql)
            sale_order_id = request.env.cr.fetchone()
            return Response("Success", status=200, id=sale_order_id)

    # @route("/api/sale_orders/<int:order_id>", methods=["PUT"], type="json", auth="public", cors="*")
    # def action_update_sale_order(self, order_id, **kwargs):
    #     data = request.get_json_data()
    #     # verified = self.verify_webhook(data, request.httprequest.headers['X-Crosify-Hmac-SHA256'])
    #     verified = True
    #     if not verified:
    #         return Response("Bad Request", status=400)
    #     else:
