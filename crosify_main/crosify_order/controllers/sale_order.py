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
    'ProductID': 'myadmin_product_id',
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
        digest = hmac.new(CLIENT_SECRET.encode('utf-8'), str(data), digestmod=hashlib.sha256).digest()
        hexdigest = hmac.new(CLIENT_SECRET.encode('utf-8'), str(data).encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        computed_hmac = base64.b64encode(digest)

        return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

    @route("/api/sale_orders", methods=["POST"], type="json", auth="public", cors="*")
    def action_create_sale_order(self, **kwargs):
        data = request.get_json_data()
        verified = self.verify_webhook(data, request.httprequest.headers['X-Signature-SHA256'])
        # verified = True
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
            insert into res_partner(name, complete_name,street,street2,city,state_id,zip,country_id,phone,mobile,email) 
            values (
            '{data.get('ShippingFirstname', '')} {data.get('ShippingLastname', '')}', 
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
                partner_id,
                partner_invoice_id,
                partner_shipping_id,
                date_order
--                 warehouse_id,
--                 picking_policy
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
                       '{data.get('TrackingUrl', '')}', {request.env(su=True).company.id}, {partner_id}, {partner_id}, {partner_id}, now() 
             Returning id
            """
            request.env.cr.execute(create_order_sql)
            sale_order_id = request.env.cr.fetchone()
            order_lines = data.get('Details', [])
            for line in order_lines:
                quantity = line.get('Quantity', 0)
                create_order_line_sql = f"""
                insert into sale_order_line(
                my_admin_detailed_id,
                my_admin_order_id,
                order_id_fix,
                myadmin_product_id,
                meta_field,
                price_unit,
                product_uom_qty,
                price_subtotal,
                crosify_discount_amount,
                total_tax,
                shipping_cost,
                tips,
                price_total,
                cost_amount,
                status,
                sublevel_id,
                customer_note,
                product_id,
                personalize,
                element_message,
                design_date,
                extra_service,
                note_fulfill,
                fulfill_date,
                priority,
                packed_date,
                pickup_date,
                deliver_status,
                deliver_date,
                description_item_size,
                box_size,
                package_size,
                product_code,
                design_serial_number,
                color_set_name,
                accessory_name,
                color_item,
                logistic_cost,
                hs_code,
                tkn_code,
                upload_tkn_date,
                upload_tkn_by,
                tkn_url,
                is_upload_tkn,
                note_change_request,
                dispute_status,
                dispute_note,
                crosify_approve_cancel_employee_id,
                cancel_date,
                cancel_reason,
                cancel_status,
                update_date,
                crosify_created_date,
                crosify_create_by,
                last_update_level_date,
                packaging_location,
                shipping_method,
                order_id, 
                name,
                customer_lead,
                product_uom
                ) 
                values
                """
                price_subtotal = round(line.get('Subtotal', 0) / quantity, 2)
                discount = round(line.get('Discount', 0) / quantity, 2)
                total_tax = round(line.get('Totaltax', 0) / quantity, 2)
                shipping_cost = round(line.get('ShippingCost', 0) / quantity, 2)
                price_total = round(line.get('TotalAmount', 0) / quantity, 2)
                tip = round(line.get('Tip', 0) / quantity, 2)
                sub_level = request.env['sale.order.line.level'].sudo().search(
                    [('level', '=', line.get('LevelCode', '0'))], limit=1)
                product_id = request.env['product.product'].sudo().search([('default_code', '=', line.get('Sku', ''))],
                                                                          limit=1)
                upload_tkn_by = request.env['hr.employee'].sudo().search(
                    [('work_email', '=', line.get('UploadTknBy', ''))], limit=1)
                crosify_approve_cancel_employee_id = request.env['hr.employee'].sudo().search(
                    [('work_email', '=', line.get('ApproveCancelBy', ''))], limit=1)
                for sub_item in range(quantity):
                    if sub_item > 0:
                        create_order_line_sql += ","
                    create_order_line_sql += f"""
                    (
                    {line.get('Detailid', 0)},
                    {line.get('Orderid', 0)},
                    '{line.get('OrderidFix', 0)}',
                    {line.get('ProductID', 0)},
                    {line.get('meta_field', 0)},
                    {line.get('Amount', 0)},
                    1,
                    {price_subtotal},
                    {discount},
                    {total_tax},
                    {shipping_cost},
                    {tip},
                    {price_total},
                    {line.get('CostAmount', 0)},
                    '{line.get('Status', '')}',
                    """
                    if not sub_level:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                {sub_level.id},
                                                """

                    create_order_line_sql += f"""
                    '{line.get('CustomerNote', '')}',
                    """
                    if not product_id:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                {product_id.id},
                                                """
                    create_order_line_sql += f"""
                    '{line.get('Personalize', '')}',
                    '{line.get('ElementMessage', '')}',
                    """

                    if line.get('DesignDate') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('DesignDate', '')}',
                                                """

                    create_order_line_sql += f"""
                    
                    '{line.get('ExtraService', '')}',
                    '{line.get('FulfillNote', '')}',
                    '{line.get('FulfillDate', '')}',
                    {line.get('Priority', '')},
                    """

                    if line.get('PackedDate') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('PackedDate', '')}',
                                                """
                    if line.get('PickupDate') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('PickupDate', '')}',
                                                """

                    create_order_line_sql += f"""
                    '{line.get('DeliveryStatus', '')}',
                    """

                    if line.get('DeliveryUpdateDate') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('DeliveryUpdateDate', '')}',
                                                """

                    create_order_line_sql += f"""
                    '{line.get('DescriptionItemSize', '')}',
                    '{line.get('Boxsize', '')}',
                    '{line.get('Packagesize', '')}',
                    '{line.get('Productcode', '')}',
                    '{line.get('DesignSerialno', '')}',
                    '{line.get('ColorsetName', '')}',
                    '{line.get('AccessoryName', '')}',
                    '{line.get('ColorItem', '')}',
                    {line.get('LogisticCost', '')},
                    '{line.get('HScode', '')}',
                    '{line.get('TKN', '')}',
                    
                    """

                    if line.get('UploadTknat') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('UploadTknat', '')}',
                                                """

                    if not upload_tkn_by:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                {upload_tkn_by.id},
                                                """


                    create_order_line_sql += f"""
                    '{line.get('TrackingUrl', '')}',
                    {line.get('IsUploadTKN', '')},
                    '{line.get('ChangeRequestNote', '')}',
                    '{line.get('DisputeStatus', '')}',
                    '{line.get('DisputeNote', '')}',
                    """
                    if not crosify_approve_cancel_employee_id:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                {crosify_approve_cancel_employee_id.id},
                                                """


                    if line.get('Canceledat') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('Canceledat', '')}',
                                                """

                    create_order_line_sql += f"""
                    '{line.get('CancelReason', '')}',
                    '{line.get('CancelStatus', '')}',
                    """

                    if line.get('Updatedat') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('Updatedat', '')}',
                                                """

                    if line.get('Createdat') is None:
                        create_order_line_sql += "null,"

                    else:
                        create_order_line_sql += f"""
                                                '{line.get('Createdat', '')}',
                                                """

                    create_order_line_sql += f"""
                    '{line.get('CreatedBy', '')}',
                    """

                    if line.get('LastupdateLevel') is None:

                        create_order_line_sql += "null,"
                    else:
                        create_order_line_sql += f"""
                                                '{line.get('LastupdateLevel', '')}',
                                                """

                    create_order_line_sql += f"""
                    '{line.get('PackagingLocationInfo', '')}',
                    '{line.get('ShippingMethodInfo', '')}',
                    {sale_order_id[0]},
                    '{product_id.display_name}',
                    0,
                    1
                    )
                    """
                request.env.cr.execute(create_order_line_sql)
            response = {
                'status': 200,
                'message': 'Created Order',
                'data': {
                    'order_id': sale_order_id
                }
            }
            return response
            # return Response("Success", status=200)

    @route("/api/sale_orders/<int:my_admin_order_id>", methods=["PUT"], type="json", auth="public", cors="*")
    def action_update_sale_order(self, my_admin_order_id, **kwargs):
        data = request.get_json_data()
        # verified = self.verify_webhook(data, request.httprequest.headers['X-Crosify-Hmac-SHA256'])
        verified = True
        if not verified:
            return Response("Bad Request", status=400)
        else:
            sale_order = request.env['sale.order'].sudo().search([('myadmin_order_id', '=', my_admin_order_id)], limit=1)
            if not sale_order.exists():
                response = {
                    'status': 400,
                    'message': 'Order not found',
                }
                return response
            state_id = request.env['res.country.state'].sudo().search([('code', '=', data.get('StateCode'))], limit=1)
            country_id = request.env['res.country'].sudo().search([('code', '=', data.get('CountryCode'))], limit=1)
            currency_id = request.env['res.currency'].sudo().search([('name', '=', data.get('Currency'))], limit=1)
            order_update_employee = request.env['hr.employee'].sudo().search([('work_email', '=', data.get('UpdatedBy'))], limit=1)
            order_create_employee = request.env['hr.employee'].sudo().search([('work_email', '=', data.get('CreatedBy'))], limit=1)

            update_order_sql = f"""
            update sale_order 
            set name = '{data.get('Name', '')}',
                myadmin_order_id = '{data.get('Orderid', '')}',
                transaction_id = '{data.get('Transactionid', '')}',
                channel_ref_id = '{data.get('ChannelRefID', '')}',
                shipping_firstname = '{data.get('ShippingFirstname', '')}',
                shipping_lastname = '{data.get('ShippingLastname', '')}',
                shipping_address = '{data.get('ShippingAddress', '')}',
                shipping_city = '{data.get('ShippingCity', '')}',
                shipping_zipcode = '{data.get('shipping_zipcode', '')}',
                shipping_country_id = {country_id.id if country_id else 'null'},
                shipping_state_id = {state_id.id if state_id else 'null'},
                shipping_phone_number = '{data.get('ShippingPhonenumber', '')}',
                shipping_apartment = '{data.get('ShippingApartment', '')}',
                contact_email = '{data.get('ContactEmail', '')}',
                note = '{data.get('CustomerNote', '')}',
                client_secret = '{data.get('ClientSecret', '')}',
                domain = '{data.get('Domain', '')}',
                tip = {data.get('Tip') if data.get('Tip') is not None else 0},
                shipping_cost = {data.get('ShippingCost') if data.get('ShippingCost') is not None else 0},
                amount_untaxed = {data.get('Subtotal') if data.get('Subtotal') is not None else 0},
                discount  = {data.get('Discount') if data.get('Discount') is not None else 0},
                amount_total = {data.get('TotalAmount') if data.get('TotalAmount') is not None else 0},
                currency_id = {currency_id.id if currency_id else 'null'},
                payment_status = '{data.get('PaymentStatus', '')}',
                payment_note = '{data.get('PaymentNote', '')}',
                discount_code = '{data.get('DiscountCode', '')}',
                logistic_cost = {data.get('LogisticCost') if data.get('LogisticCost') is not None else 0},
                rating = '{data.get('rating', '')}',
                review = '{data.get('review', '')}',
                crosify_updated_by = {order_update_employee.id if order_update_employee else 'null'},
                crosify_create_by = {order_create_employee.id if order_create_employee else 'null'},
                tkn = '{data.get('Tkn', '')}',
                is_upload_tkn = {data.get('IsUploadTKN', )},
                tkn_url = '{data.get('TrackingUrl', '')}'
            
            """

            if sale_order.partner_id.phone != data.get('ShippingPhonenumber'):
                partner_sql = f"""
                            insert into res_partner(name, complete_name,street,street2,city,state_id,zip,country_id,phone,mobile,email) 
                            values (
                            '{data.get('ShippingFirstname', '')} {data.get('ShippingLastname', '')}', 
                            '{data.get('ShippingFirstname', '')} {data.get('ShippingLastname', '')}', 
                            '{data.get('ShippingAddress', '')}',
                            '{data.get('ShippingApartment', '')}',
                            '{data.get('ShippingCity', '')}',
                            {state_id.id},
                            '{data.get('ShippingZipcode', '')}',
                            {country_id.id},
                            '{data.get('ShippingPhonenumber', '')}',
                            '{data.get('ShippingPhonenumber', '')}',
                            '{data.get('ContactEmail', '')}'
                            ) 
                            returning id
                            """

                request.env.cr.execute(partner_sql)
                partner_id = request.env.cr.fetchone()[0]
                update_order_sql += f"""
                , partner_id = {partner_id}
                """
            update_order_sql += f"""
            where id = {order_id}
            
            """

            request.env.cr.execute(update_order_sql)

            order_lines = data.get('Details', [])
            for line in order_lines:
                sub_level = request.env['sale.order.line.level'].sudo().search(
                    [('level', '=', line.get('LevelCode', '0'))], limit=1)
                product_id = request.env['product.product'].sudo().search([('default_code', '=', line.get('Sku', ''))],
                                                                          limit=1)
                upload_tkn_by = request.env['hr.employee'].sudo().search(
                    [('work_email', '=', line.get('UploadTknBy', ''))], limit=1)
                crosify_approve_cancel_employee_id = request.env['hr.employee'].sudo().search(
                    [('work_email', '=', line.get('ApproveCancelBy', ''))], limit=1)
                quantity = line.get('Quantity', 0)
                detail_id = line.get('Detailid') if line.get('Detailid') is not None else 0
                update_order_line_sql = f"""
                update sale_order_line 
                set 
                my_admin_detailed_id = {detail_id},
                my_admin_order_id = {line.get('Orderid', 0) if line.get('Orderid', 0) is not None else 'null'},
                order_id_fix = '{line.get('OrderidFix') if line.get('OrderidFix') is not None else 'null'}',
                myadmin_product_id = {line.get('ProductID') if line.get('ProductID') is not None else 'null'},
                meta_field = {line.get('meta_field') if line.get('meta_field') is not None else 'null'},
                price_unit = {line.get('Amount') if line.get('Amount') is not None else 'null'},
                product_uom_qty = 1,
                price_subtotal = {round(line.get('Subtotal', 0) / quantity, 2)},
                crosify_discount_amount = {round(line.get('Discount', 0) / quantity, 2)},
                total_tax = {round(line.get('Totaltax', 0) / quantity, 2)},
                shipping_cost = {round(line.get('ShippingCost', 0) / quantity, 2)},
                tips = {round(line.get('Tip', 0) / quantity, 2)},
                price_total = {round(line.get('TotalAmount', 0) / quantity, 2)},
                cost_amount = {line.get('CostAmount') if line.get('CostAmount', 0) is not None else 0},
                """
                if line.get('Status') is not None:
                    update_order_line_sql += f"""
                    status = {line.get('Status')},
                    """
                else:
                    update_order_line_sql += f"""
                                        status = null,
                                        """

                update_order_line_sql += f"""
                sublevel_id = {sub_level.id if sub_level else 'null'},
                level_id = {sub_level.parent_id.id if sub_level and sub_level.parent_id else 'null'},
                customer_note = '{line.get('CustomerNote') if line.get('CustomerNote') is not None else 'null'}',
                product_id = {product_id.id if product_id else 'null'},
                personalize = '{line.get('Personalize') if line.get('Personalize') is not None else 'null'}',
                element_message = '{line.get('ElementMessage') if line.get('ElementMessage') is not None else 'null'}',
                design_date = '{line.get('DesignDate') if line.get('DesignDate') is not None else 'null'}',
                extra_service = '{line.get('ExtraService') if line.get('ExtraService') is not None else 'null'}',
                note_fulfill = '{line.get('FulfillNote') if line.get('FulfillNote') is not None else 'null'}',
                fulfill_date = '{line.get('FulfillDate') if line.get('FulfillDate') is not None else 'null'}',
                priority = '{line.get('Priority') if line.get('Priority') is not None else 'null'}',
                packed_date = '{line.get('PackedDate') if line.get('PackedDate') is not None else 'null'}',
                pickup_date = '{line.get('PackedDate') if line.get('PackedDate') is not None else 'null'}',
                deliver_status = '{line.get('PickupDate') if line.get('PickupDate') is not None else 'null'}',
                deliver_date = '{line.get('DeliveryUpdateDate') if line.get('DeliveryUpdateDate') is not None else 'null'}',
                description_item_size = '{line.get('DescriptionItemSize') if line.get('DescriptionItemSize') is not None else 'null'}',
                box_size = '{line.get('Boxsize') if line.get('Boxsize') is not None else 'null'}',
                package_size = '{line.get('Packagesize') if line.get('Packagesize') is not None else 'null'}',
                product_code = '{line.get('Productcode') if line.get('Productcode') is not None else 'null'}',
                design_serial_number = '{line.get('DesignSerialno') if line.get('DesignSerialno') is not None else 'null'}',
                color_set_name = '{line.get('ColorsetName') if line.get('ColorsetName') is not None else 'null'}',
                accessory_name = '{line.get('AccessoryName') if line.get('AccessoryName') is not None else 'null'}',
                color_item = '{line.get('ColorItem') if line.get('ColorItem') is not None else 'null'}',
                logistic_cost = {line.get('LogisticCost') if line.get('LogisticCost') is not None else 'null'},
                hs_code = '{line.get('HScode') if line.get('HScode') is not None else 'null'}',
                tkn_code = '{line.get('TKN') if line.get('TKN') is not None else 'null'}',
                upload_tkn_date = '{line.get('UploadTknat') if line.get('UploadTknat') is not None else 'null'}',
                upload_tkn_by = {upload_tkn_by.id if upload_tkn_by else 'null'},
                tkn_url = '{line.get('TrackingUrl') if line.get('TrackingUrl') is not None else 'null'}',
                is_upload_tkn = '{line.get('IsUploadTKN') if line.get('IsUploadTKN') is not None else 'null'}',
                note_change_request = '{line.get('ChangeRequestNote') if line.get('ChangeRequestNote') is not None else 'null'}',
                dispute_status = '{line.get('DisputeStatus') if line.get('DisputeStatus') is not None else 'null'}',
                dispute_note = '{line.get('DisputeNote') if line.get('DisputeNote') is not None else 'null'}',
                crosify_approve_cancel_employee_id = {crosify_approve_cancel_employee_id.id if crosify_approve_cancel_employee_id else 'null'},
                cancel_date = '{line.get('Canceledat') if line.get('Canceledat') is not None else 'null'}',
                cancel_reason = '{line.get('CancelReason') if line.get('CancelReason') is not None else 'null'}',
                cancel_status = '{line.get('CancelStatus') if line.get('CancelStatus') is not None else 'null'}',
                """

                if line.get('Updatedat') is not None:
                    update_order_line_sql += f"""
                    update_date = '{line.get('Updatedat')}',
                    """
                else:
                    update_order_line_sql += f"""
                                        update_date = null,
                                        """


                if line.get('Createdat') is not None:
                    update_order_line_sql += f"""
                    crosify_created_date = '{line.get('Createdat')}',
                    """
                else:
                    update_order_line_sql += f"""
                                        crosify_created_date = null,
                                        """

                update_order_line_sql += f"""
                crosify_create_by = '{line.get('CreatedBy') if line.get('CreatedBy') is not None else 'null'}',
                last_update_level_date = '{line.get('LastupdateLevel') if line.get('LastupdateLevel') is not None else 'null'}',
                packaging_location = '{line.get('PackagingLocationInfo') if line.get('PackagingLocationInfo') is not None else 'null'}',
                shipping_method = '{line.get('ShippingMethodInfo') if line.get('ShippingMethodInfo') is not None else 'null'}', 
                name = '{product_id.display_name}' 
                where my_admin_detailed_id = {detail_id} 
                """

                request.env.cr.execute(update_order_line_sql)

            response = {
                'status': 200,
                'message': 'Updated Order',
                'data': {
                    'order_id': order_id
                }
            }
            return response
