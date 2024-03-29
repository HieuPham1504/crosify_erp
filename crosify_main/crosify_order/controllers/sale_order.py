# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import http
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
    'ProductionLine': 'production_line_id',

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

    def verify_webhook(self):
        ip_whitelist = request.env['ir.config_parameter'].sudo().get_param('api.ip.whitelist')
        if not ip_whitelist:
            return False
        else:
            ip_whitelist_ids = [ip.strip() for ip in ip_whitelist.split(',')]
            current_ip = request.httprequest.environ['REMOTE_ADDR']
            result = True if current_ip in ip_whitelist_ids else False
            return result


    @route("/api/sale_orders", methods=["POST"], type="json", auth="public", cors="*")
    def action_create_sale_order(self, **kwargs):
        now = datetime.now()
        now_plus_7_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        data = request.get_json_data()
        remote_ip = request.httprequest.environ['REMOTE_ADDR']
        verified = self.verify_webhook()
        if not verified:
            response = {
                'status': 404,
                'message': 'Not Found',
            }
            return response
        else:
            try:
                if data.get('Name') is not None:
                    duplicate_name_order = request.env['sale.order'].sudo().search([('name', '=', data.get('Name'))])
                    if duplicate_name_order:
                        response = {
                            'status': 404,
                            'message': 'Order Name has already exists.',
                        }
                        insert_log_sql = f"""
                                        INSERT INTO sale_order_sync(sale_order_id,description,create_date,status,response, type,description_json,remote_ip_address) 
                                        VALUES (
                                        null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', 'Order Name has already exists.', 'create', '{json.dumps(data)}'::json, '{remote_ip}'
                                        ) 
                                        """
                        request.env.cr.execute(insert_log_sql)
                        return response
                shipping_country = request.env['res.country'].sudo().search([('code', '=', data.get('CountryCode'))],
                                                                            limit=1)
                shipping_country_id = shipping_country.id

                shipping_state = request.env['res.country.state'].sudo().search(
                    [('code', '=', data.get('StateCode')), ('country_id', '=', shipping_country_id)], limit=1)

                shipping_state_id = shipping_state.id

                Partner = request.env['res.partner'].sudo()
                first_name = data.get('ShippingFirstname') if data.get('ShippingFirstname') is not None else ''
                last_name = data.get('ShippingLastname') if data.get('ShippingLastname') is not None else ''
                partner_id = Partner.create({
                    'name': f"{first_name} {last_name}",
                    'complete_name': f"{first_name} {last_name}",
                    'street': data.get('ShippingAddress') if data.get('ShippingAddress') is not None else '',
                    'street2': data.get('ShippingApartment') if data.get('ShippingApartment') is not None else '',
                    'city': data.get('ShippingCity') if data.get('ShippingCity') is not None else '',
                    'state_id': shipping_state_id,
                    'zip': data.get('ShippingZipcode') if data.get('ShippingZipcode') is not None else '',
                    'country_id': shipping_country_id,
                    'phone': data.get('ShippingPhonenumber') if data.get('ShippingPhonenumber') is not None else '',
                    'mobile': data.get('ShippingPhonenumber') if data.get('ShippingPhonenumber') is not None else '',
                    'email': data.get('ContactEmail') if data.get('ContactEmail') is not None else '',
                    'active': True,
                    'partner_type_id': request.env.ref('crosify_order.customer_partner_type').id,
                })

                order_type_id = request.env['sale.order.type'].sudo().search([('order_type_name', '=', 'Normal')],
                                                                             limit=1)
                payment_method = False
                if data.get('PaymentMethod') is not None:
                    payment_method = request.env['payment.method'].sudo().search(
                        [('code', '=ilike', data.get('PaymentMethod').strip())], limit=1)
                utm_source = False
                if data.get('UtmSource') is not None:
                    utm_source = request.env['utm.source'].sudo().search(
                        [('name', '=ilike', data.get('UtmSource').strip())], limit=1)

                seller_id = request.env['crosify.seller'].sudo().search(
                    [('code', '=', data.get('SellerCode'))], limit=1)
                if data.get('ShippingLine') is None:
                    shipping_line_id = request.env['order.shipping.line']
                else:
                    shipping_line_id = request.env['order.shipping.line'].sudo().search(
                        [('code', '=', data.get('ShippingLine'))], limit=1)
                    if not shipping_line_id:
                        shipping_line_id = request.env['order.shipping.line'].sudo().create({
                            'code': data.get('ShippingLine'),
                            'name': data.get('ShippingLine'),
                        })
                currency = data.get('Currency').upper() if data.get('Currency') is not None else ''
                create_order_sql = f"""
                    with currency as (
                        select id 
                        from res_currency 
                        where name = '{currency}' 
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
                    order_id_fix,
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
                    date_order,
                    order_type_id, 
                    order_payment_state,
                    payment_method_id,
                    utm_source_id, 
                    create_date, 
                    amount_tax,
                    seller_id,
                    shipping_line_id
    --                 warehouse_id,
    --                 picking_policy
                    ) 
                    Select '{data.get('Name', '')}',
                     '{data.get('Orderid') if not data.get('Orderid') is None else ''}', 
                     '{data.get('Orderid', '') if not data.get('Orderid') is None else ''}', 
                     '{data.get('Transactionid') if not data.get('Transactionid') is None else ''}', 
                     '{data.get('ChannelRefID') if not data.get('ChannelRefID') is None else ''}', 
                     '{data.get('ShippingFirstname') if not data.get('ShippingFirstname') is None else ''}',
                       '{data.get('ShippingLastname') if not data.get('ShippingLastname') is None else ''}', 
                       '{data.get('ShippingAddress') if not data.get('ShippingAddress') is None else ''}', 
                       '{data.get('ShippingCity') if not data.get('ShippingCity') is None else ''}', 
                       '{data.get('ShippingZipcode') if not data.get('ShippingZipcode') is None else ''}', 
                       {shipping_country_id}, 
                       {shipping_state_id}, 
                       '{data.get('ShippingPhonenumber') if not data.get('ShippingPhonenumber') is None else ''}', 
                       '{data.get('ShippingApartment') if not data.get('ShippingApartment') is None else ''}', 
                       '{data.get('ContactEmail') if not data.get('ContactEmail') is None else ''}', 
                       '{data.get('CustomerNote') if not data.get('CustomerNote') is None else ''}',
                       '{data.get('ClientSecret') if not data.get('ClientSecret') is None else ''}', 
                       '{data.get('Domain') if not data.get('Domain') is None else ''}', 
                       {data.get('Tip') if not data.get('Tip') is None else 0}, 
                       {data.get('ShippingCost') if not data.get('ShippingCost') is None else 0}, 
                       {data.get('Subtotal') if not data.get('Subtotal') is None else 0},
                       {data.get('Discount') if not data.get('Discount') is None else 0}, 
                       {data.get('TotalAmount') if not data.get('TotalAmount') is None else 0}, 
                       """
                if data.get('Paymentat') is None:

                    create_order_sql += "null,"
                else:
                    create_order_sql += f"""
                                            '{data.get('Paymentat', '')}',
                                            """
                create_order_sql += f"""
                         
                       (select currency.id from currency), 
                       '{data.get('PaymentStatus') if not data.get('PaymentStatus') is None else ''}', 
                       '{data.get('PaymentNote') if not data.get('PaymentNote') is None else ''}', 
                       '{data.get('DiscountCode') if not data.get('DiscountCode') is None else ''}',  
                           """
                if data.get('LogisticCost') is not None:
                    create_order_sql += f"""
                               '{data.get('LogisticCost', False)}', """
                else:
                    create_order_sql += "0,"

                create_order_sql += f"""
                           '{data.get('rating', '')}', '{data.get('review', '')}', 
                           """
                if data.get('Updatedat') is None:

                    create_order_sql += "null,"
                else:
                    create_order_sql += f"""
                                            '{data.get('Updatedat', '')}',
                                            """

                create_order_sql += f"""(select order_update_employee.id from order_update_employee),
                           '{data.get('Createdat')}', 
                           (select order_create_employee.id from order_create_employee), 
                           '{data.get('Tkn') if not data.get('Tkn') is None else ''}', 
                           {data.get('IsUploadTKN', ) if not data.get('IsUploadTKN', ) is None else 'null'}, 
                           '{data.get('TrackingUrl', '') if not data.get('TrackingUrl') is None else ''}', 
                           {request.env(su=True).company.id}, 
                           {partner_id.id}, 
                           {partner_id.id}, 
                           {partner_id.id}, 
                           now(), 
                           {order_type_id.id if order_type_id else 'null'}, 
                           '{'paid' if data.get('PaymentStatus') == 1 else 'not_paid'}',
                           {payment_method.id if payment_method else 'null'},
                           {utm_source.id if utm_source else 'null'}, 
                           now(), 
                           {data.get('TaxPrice') if not data.get('TaxPrice') is None else 0},
                           {seller_id.id if seller_id else 'null'},
                           {shipping_line_id.id if shipping_line_id else 'null'}
                 Returning id
                """
                request.env.cr.execute(create_order_sql)
                sale_order_id = request.env.cr.fetchone()
                order_lines = data.get('Details', [])
                self.action_insert_item(sale_order_id[0], partner_id, data, order_lines)

                response = {
                    'status': 200,
                    'message': 'Created Order',
                    'data': {
                        'order_id': sale_order_id[0]
                    }
                }
                return response
            except Exception as e:
                e_str = e.args[0].replace("'", "") if e.args else ''
                insert_log_sql = f"""
                INSERT INTO sale_order_sync(sale_order_id,description,create_date,status, type,description_json,remote_ip_address,response) 
                VALUES (
                null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', 'create', '{json.dumps(data)}'::json, '{remote_ip}', '{e_str}'
                ) 
                """
                request.env.cr.execute(insert_log_sql)
                request.env.cr.execute(f"delete from sale_order where order_id_fix = '{data.get('Orderid')}'")
                response = {
                    'status': 400,
                    'message': f'{e.__class__.__name__}: {e_str}',
                }

                return response

    def action_insert_item(self, sale_order_id, partner_id, data, order_lines):
        now = datetime.now()
        now_plus_7_str = now.strftime("%Y-%m-%dT%H:%M:%S")

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
            product_sku,
            personalize,
            element_message,
            design_date,
            extra_service,
            note_fulfill,
            fulfill_order_date,
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
            cancel_note,
            update_date,
            crosify_created_date,
            crosify_create_by,
            last_update_level_date,
            packaging_location,
            shipping_method,
            order_id, 
            name,
            product_type,
            customer_lead,
            product_uom,
            company_id,
            currency_id,
            order_partner_id,
            variant, 
            create_date,
            is_combo,
            production_line_id,
            order_index
            ) 
            values
            """
            total_discount = line.get('Discount') if line.get('Discount') is not None else 0
            total_subtotal = line.get('Subtotal') if line.get('Subtotal') is not None else 0
            total_tax = line.get('Totaltax') if line.get('Totaltax') is not None else 0
            total_shipping_cost = line.get('ShippingCost') if line.get('ShippingCost') is not None else 0
            total_amount = line.get('TotalAmount') if line.get('TotalAmount') is not None else 0
            total_tip = line.get('Tip') if line.get('Tip') is not None else 0


            price_subtotal = round(total_subtotal / quantity, 2)
            discount = round(total_discount / quantity, 2)
            total_tax = round(total_tax / quantity, 2)
            shipping_cost = round(total_shipping_cost / quantity, 2)
            price_total = round(total_amount / quantity, 2)
            tip = round(total_tip / quantity, 2)

            if line.get('ProductionLine') is None:
                production_line_id = request.env['item.production.line']
            else:
                production_line_id = request.env['item.production.line'].sudo().search(
                    [('code', '=', line.get('ProductionLine'))], limit=1)
                if not production_line_id:
                    production_line_id = request.env['item.production.line'].sudo().create({
                        'code': line.get('ProductionLine'),
                        'name': line.get('ProductionLine'),
                    })

            PaymentStatus = data.get('PaymentStatus')
            if PaymentStatus == 1:
                level_code = 'L1.1'
            else:
                level_code = 'L0'
            sub_level = request.env['sale.order.line.level'].sudo().search(
                [('level', '=', level_code)], limit=1)
            product_id = request.env['product.product'].sudo().search(
                [('default_code', '=', line.get('Sku', ''))],
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
                {line.get('Detailid', 0) if line.get('Detailid') is not None else 0},
                {line.get('Orderid', 0) if line.get('Orderid') is not None else 0},
                '{data.get('Orderid') if not data.get('Orderid') is None else ''}',
                {line.get('ProductID') if line.get('ProductID') is not None else 0},
                '{line.get('Metafield') if line.get('Metafield') is not None else ''}',
                {line.get('Amount') if line.get('Amount') is not None else 0},
                1,
                {price_subtotal},
                {discount},
                {total_tax},
                {shipping_cost},
                {tip},
                {price_total},
                {line.get('CostAmount') if line.get('CostAmount') is not None else 0},
                '{line.get('Status') if line.get('Status') is not None else ''}',
                """
                if not sub_level:

                    create_order_line_sql += "null,"
                else:
                    create_order_line_sql += f"""
                                            {sub_level.id},
                                            """

                create_order_line_sql += f"""
                '{line.get('CustomerNote') if line.get('CustomerNote') is not None else ''}',
                """
                none_product_id = request.env(su=True).ref('crosify_order.product_product_fail_data')
                if not product_id:
                    create_order_line_sql += f"{none_product_id.id},"
                else:
                    create_order_line_sql += f"""
                                            {product_id.id},
                                            """

                if not product_id:
                    create_order_line_sql += f"'{none_product_id.default_code}',"
                else:
                    create_order_line_sql += f"""
                                            '{product_id.default_code}',
                                            """

                create_order_line_sql += f"""
                '{line.get('Personalize') if line.get('Personalize') is not None else ''}',
                '{line.get('ElementMessage') if line.get('ElementMessage') is not None else ''}',
                """

                if line.get('DesignDate') is None:

                    create_order_line_sql += "null,"
                else:
                    create_order_line_sql += f"""
                                            '{line.get('DesignDate', '')}',
                                            """

                create_order_line_sql += f"""

                '{line.get('ExtraService') if line.get('ExtraService') is not None else ''}',
                '{line.get('FulfillNote') if line.get('FulfillNote') is not None else ''}',
                """

                if line.get('FulfillDate') is None:

                    create_order_line_sql += "null,"
                else:
                    create_order_line_sql += f"""
                                            '{line.get('FulfillDate', '')}',
                                            """

                create_order_line_sql += f"""
                {line.get('Priority', 'false')},
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
                '{line.get('DescriptionItemSize') if line.get('DescriptionItemSize') is not None else ''}',
                '{line.get('Boxsize') if line.get('Boxsize') is not None else ''}',
                '{line.get('Packagesize') if line.get('Packagesize') is not None else ''}',
                '{line.get('Productcode') if line.get('Productcode') is not None else ''}',
                '{line.get('DesignSerialno') if line.get('DesignSerialno') is not None else ''}',
                '{line.get('ColorsetName') if line.get('ColorsetName') is not None else ''}',
                '{line.get('AccessoryName') if line.get('AccessoryName') is not None else ''}',
                '{line.get('ColorItem') if line.get('ColorItem') is not None else ''}',
                {line.get('LogisticCost') if line.get('LogisticCost') is not None else 0},
                '{line.get('HScode') if line.get('HScode') is not None else ''}',
                '{line.get('TKN') if line.get('TKN') is not None else ''}',

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
                '{line.get('TrackingUrl') if line.get('TrackingUrl') is not None else ''}',
                {line.get('IsUploadTKN') if line.get('IsUploadTKN') is not None else 'false'},
                '{line.get('ChangeRequestNote') if line.get('ChangeRequestNote') is not None else ''}',
                '{line.get('DisputeStatus') if line.get('DisputeStatus') is not None else ''}',
                '{line.get('DisputeNote') if line.get('DisputeNote') is not None else ''}',
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
                '{line.get('CancelReason') if line.get('CancelReason') is not None else ''}',
                """

                if line.get('Updatedat') is None:

                    create_order_line_sql += "null,"
                else:
                    create_order_line_sql += f"""
                                            '{line.get('Updatedat', '')}',
                                            """

                if data.get('Createdat') is None:
                    create_order_line_sql += "null,"

                else:
                    create_order_line_sql += f"""
                                            '{data.get('Createdat')}',
                                            """

                create_order_line_sql += f"""
                '{line.get('CreatedBy') if line.get('CreatedBy') is not None else ''}',
                """

                if line.get('LastupdateLevel') is None:

                    create_order_line_sql += "null,"
                else:
                    create_order_line_sql += f"""
                                            '{line.get('LastupdateLevel', '')}',
                                            """

                currency = data.get('Currency').upper() if data.get('Currency') is not None else ''
                create_order_line_sql += f"""
                '{line.get('PackagingLocationInfo') if line.get('PackagingLocationInfo') is not None else ''}',
                '{line.get('ShippingMethodInfo') if line.get('ShippingMethodInfo') is not None else ''}',
                {sale_order_id},
                '{line.get('ProductName') if line.get('ProductName') is not None else ''}',
                '{product_id.product_type if product_id else none_product_id.product_type}',
                0,
                1,
                {request.env(su=True).company.id}, 
                (select id 
                from res_currency 
                where name = '{currency}' 
                limit 1),
                {partner_id.id},
                '{line.get('Variant') if line.get('Variant') is not None else ''}', 
                now(),

                """
                if quantity > 1:
                    create_order_line_sql += """ 
                    true,
                    """
                else:
                    create_order_line_sql += """ 
                                            false,
                                            """

                create_order_line_sql += f""" 
                {production_line_id.id if production_line_id else 'null'},
                {line.get('OrderIndex') if line.get('OrderIndex') is not None else 0}
                )
                """

            request.env.cr.execute(create_order_line_sql)
        remote_ip = request.httprequest.environ['REMOTE_ADDR']
        insert_log_sql = f"""
                        INSERT INTO sale_order_sync(sale_order_id,description,create_date,status, type,description_json,remote_ip_address) 
                        VALUES (
                        {sale_order_id}, '{json.dumps(data)}', '{now_plus_7_str}', 'pass', 'create', '{json.dumps(data)}'::json, '{remote_ip}'
                        ) 
                        """
        request.env.cr.execute(insert_log_sql)

    @route("/api/sale_orders/<int:my_admin_order_id>", methods=["POST"], type="json", auth="public", cors="*")
    def action_update_sale_order(self, my_admin_order_id, **kwargs):
        now = datetime.now()
        now_plus_7_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        data = request.get_json_data()
        remote_ip = request.httprequest.environ['REMOTE_ADDR']
        verified = self.verify_webhook()
        if not verified:
            response = {
                'status': 404,
                'message': 'Not Found',
            }
            return response
        else:
            try:

                sale_order = request.env['sale.order'].sudo().search([('myadmin_order_id', '=', my_admin_order_id)],
                                                                     limit=1)
                if not sale_order.exists():
                    response = {
                        'status': 400,
                        'message': 'Order not found',
                    }
                    insert_log_sql = f"""
                                                            INSERT INTO sale_order_sync(sale_order_id,description,create_date,status,response,type,description_json,remote_ip_address) 
                                                            VALUES (
                                                            null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', 'Order not found', 'update', '{json.dumps(data)}'::json, '{remote_ip}'
                                                            ) 
                                                            """
                    request.env.cr.execute(insert_log_sql)
                    return response
                else:
                    items = sale_order.order_line
                    can_not_update_levels = request.env['sale.order.line.level'].sudo().search(
                        [('can_updated_by_api', '=', True)])
                    if any(item.sublevel_id.id not in can_not_update_levels.ids for item in items):
                        response = {
                            'status': 400,
                            'message': 'Can Not Update Sale Order',
                        }
                        insert_log_sql = f"""
                                                                                    INSERT INTO sale_order_sync(sale_order_id,description,create_date,status,response,type,description_json,remote_ip_address) 
                                                                                    VALUES (
                                                                                    null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', 'Order not found', 'update', '{json.dumps(data)}'::json, '{remote_ip}'
                                                                                    ) 
                                                                                    """
                        request.env.cr.execute(insert_log_sql)
                        return response
                country_id = request.env['res.country'].sudo().search([('code', '=', data.get('CountryCode'))], limit=1)
                state_id = request.env['res.country.state'].sudo().search(
                    [('code', '=', data.get('StateCode')), ('country_id', '=', country_id.id)],
                    limit=1)
                currency_id = request.env['res.currency'].sudo().search([('name', '=', data.get('Currency'))], limit=1)
                order_update_employee = request.env['hr.employee'].sudo().search(
                    [('work_email', '=', data.get('UpdatedBy'))], limit=1)
                order_create_employee = request.env['hr.employee'].sudo().search(
                    [('work_email', '=', data.get('CreatedBy'))], limit=1)
                seller_id = request.env['crosify.seller'].sudo().search(
                    [('code', '=', data.get('SellerCode'))], limit=1)

                if data.get('ShippingLine') is None:
                    shipping_line_id = request.env['order.shipping.line']
                else:
                    shipping_line_id = request.env['order.shipping.line'].sudo().search(
                        [('code', '=', data.get('ShippingLine'))], limit=1)
                    if not shipping_line_id:
                        shipping_line_id = request.env['order.shipping.line'].sudo().create({
                            'code': data.get('ShippingLine'),
                            'name': data.get('ShippingLine'),
                        })

                update_order_sql = f"""
                update sale_order 
                set 
                    shipping_line_id = {shipping_line_id.id if shipping_line_id else 'null'},
                    seller_id = {seller_id.id if seller_id else 'null'},
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
                    amount_tax  = {data.get('TaxPrice') if data.get('Discount') is not None else 0},
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
                
                """
                if data.get('Paymentat') is not None:
                    update_order_sql += f"""
                        payment_at = '{data.get('Paymentat')}'
                    """
                else:
                    update_order_sql += f"""
                                          payment_at = null
                                        """

                partner_sql = f"""
                    update res_partner 
                    set name = '{data.get('ShippingFirstname') if data.get('ShippingFirstname') is not None else ''} {data.get('ShippingLastname') if data.get('ShippingLastname') is not None else ''}',
                        complete_name = '{data.get('ShippingFirstname') if data.get('ShippingFirstname') is not None else ''} {data.get('ShippingLastname') if data.get('ShippingLastname') is not None else ''}',
                        street = '{data.get('ShippingAddress') if data.get('ShippingAddress') is not None else ''}',
                        street2 = '{data.get('ShippingApartment') if data.get('ShippingApartment') is not None else ''}',
                        city = '{data.get('ShippingCity') if data.get('ShippingCity') is not None else ''}',
                        state_id = {state_id.id if state_id else 'null'},
                        country_id = {country_id.id if country_id else 'null'},
                        zip = '{data.get('ShippingZipcode') if data.get('ShippingZipcode') is not None else ''}',
                        phone = '{data.get('ShippingPhonenumber') if data.get('ShippingPhonenumber') is not None else ''}',
                        mobile = '{data.get('ShippingPhonenumber') if data.get('ShippingPhonenumber') is not None else ''}',
                        email = '{data.get('ContactEmail') if data.get('ContactEmail') is not None else ''}'
                        where id = {sale_order.partner_id.id}
                """

                request.env.cr.execute(partner_sql)

                update_order_sql += f"""
                where id = {sale_order.id}
                
                """

                request.env.cr.execute(update_order_sql)

                order_lines = data.get('Details', [])

                current_items = sale_order.order_line
                details_ids_param = [detail.get('Detailid') for detail in order_lines if
                                     detail.get('Detailid') is not None]

                old_lines = set(current_items.mapped('my_admin_detailed_id')) & set(details_ids_param)
                new_lines = set(details_ids_param) - set(current_items.mapped('my_admin_detailed_id'))
                delete_lines = set(current_items.mapped('my_admin_detailed_id')) - set(details_ids_param)

                if delete_lines:
                    delete_items = current_items.filtered(lambda item: item.my_admin_detailed_id in list(delete_lines))
                    delete_items.unlink()
                if new_lines:
                    new_line_ids = list(new_lines)
                    order_lines_news = [line for line in order_lines if line.get('Detailid') in new_line_ids]
                    self.action_insert_item(sale_order.id, sale_order.partner_id, data, order_lines_news)

                order_lines_old = [line for line in order_lines if line.get('Detailid') in list(old_lines)]

                for line in order_lines_old:
                    sub_level = request.env['sale.order.line.level'].sudo().search(
                        [('level', '=', line.get('LevelCode', '0'))], limit=1)
                    product_id = request.env['product.product'].sudo().search(
                        [('default_code', '=', line.get('Sku', ''))],
                        limit=1)
                    upload_tkn_by = request.env['hr.employee'].sudo().search(
                        [('work_email', '=', line.get('UploadTknBy', ''))], limit=1)
                    crosify_approve_cancel_employee_id = request.env['hr.employee'].sudo().search(
                        [('work_email', '=', line.get('ApproveCancelBy', ''))], limit=1)
                    quantity = line.get('Quantity', 0)
                    detail_id = line.get('Detailid') if line.get('Detailid') is not None else 0

                    if line.get('ProductionLine') is None:
                        production_line_id = request.env['item.production.line']
                    else:
                        production_line_id = request.env['item.production.line'].sudo().search(
                            [('code', '=', line.get('ProductionLine'))], limit=1)
                        if not production_line_id:
                            production_line_id = request.env['item.production.line'].sudo().create({
                                'code': line.get('ProductionLine'),
                                'name': line.get('ProductionLine'),
                            })

                    update_order_line_sql = f"""
                    update sale_order_line 
                    set 

                    myadmin_product_id = {line.get('ProductID') if line.get('ProductID') is not None else 'null'},
                    meta_field = '{line.get('Metafield') if line.get('Metafield') is not None else ''}',
                    variant = '{line.get('Variant') if line.get('Variant') is not None else ''}',
                    price_unit = {line.get('Amount') if line.get('Amount') is not None else 'null'},
                    product_uom_qty = 1,
                    price_subtotal = {round(line.get('Subtotal', 0) / quantity, 2)},
                    crosify_discount_amount = {round(line.get('Discount', 0) / quantity, 2)},
                    total_tax = {round(line.get('Totaltax', 0) / quantity, 2)},
                    shipping_cost = {round(line.get('ShippingCost', 0) / quantity, 2)},
                    tips = {round(line.get('Tip', 0) / quantity, 2)},
                    price_total = {round(line.get('TotalAmount', 0) / quantity, 2)},
                    cost_amount = {line.get('CostAmount') if line.get('CostAmount', 0) is not None else 0},
                    production_line_id = {production_line_id.id if production_line_id else 'null'},
                    order_index = {line.get('OrderIndex') if line.get('OrderIndex') is not None else 0},
                    """
                    if line.get('Status') is not None:
                        update_order_line_sql += f"""
                        status = {line.get('Status')},
                        """
                    else:
                        update_order_line_sql += f"""
                                            status = null,
                                            """
                    none_product_id = request.env(su=True).ref('crosify_order.product_product_fail_data')

                    update_order_line_sql += f"""
                    customer_note = '{line.get('CustomerNote') if line.get('CustomerNote') is not None else 'null'}',
                    product_id = {product_id.id if product_id else none_product_id.id},
                    personalize = '{line.get('Personalize') if line.get('Personalize') is not None else 'null'}',
                    element_message = '{line.get('ElementMessage') if line.get('ElementMessage') is not None else 'null'}',
                    extra_service = '{line.get('ExtraService') if line.get('ExtraService') is not None else 'null'}',
                    priority = '{line.get('Priority') if line.get('Priority') is not None else 'null'}',
                    deliver_status = '{line.get('PickupDate') if line.get('PickupDate') is not None else 'null'}',
                    
                    """

                    if line.get('DeliveryUpdateDate') is not None:
                        update_order_line_sql += f"""
                        deliver_date = '{line.get('DeliveryUpdateDate')}',
                        """
                    else:
                        update_order_line_sql += f"""
                                            deliver_date = null,
                                            """

                    update_order_line_sql += f"""
                    logistic_cost = {line.get('LogisticCost') if line.get('LogisticCost') is not None else 'null'},
                    note_change_request = '{line.get('ChangeRequestNote') if line.get('ChangeRequestNote') is not None else 'null'}',
                    dispute_status = '{line.get('DisputeStatus') if line.get('DisputeStatus') is not None else 'null'}',
                    dispute_note = '{line.get('DisputeNote') if line.get('DisputeNote') is not None else 'null'}',
                    crosify_approve_cancel_employee_id = {crosify_approve_cancel_employee_id.id if crosify_approve_cancel_employee_id else 'null'},
                    
                    """

                    if line.get('Canceledat') is not None:
                        update_order_line_sql += f"""
                        cancel_date = '{line.get('Canceledat')}',
                        """
                    else:
                        update_order_line_sql += f"""
                                            cancel_date = null,
                                            """

                    update_order_line_sql += f"""
                    cancel_note = '{line.get('CancelReason') if line.get('CancelReason') is not None else ''}',
                    """

                    if line.get('Updatedat') is not None:
                        update_order_line_sql += f"""
                        update_date = '{line.get('Updatedat')}',
                        """
                    else:
                        update_order_line_sql += f"""
                                            update_date = null,
                                            """

                    if line.get('LastupdateLevel') is not None:
                        update_order_line_sql += f"""
                        last_update_level_date = '{line.get('LastupdateLevel')}'
                        """
                    else:
                        update_order_line_sql += f"""
                                            last_update_level_date = null
                                            """

                    update_order_line_sql += f"""
 
                    where my_admin_detailed_id = {detail_id} 
                    """

                    request.env.cr.execute(update_order_line_sql)

                insert_log_sql = f"""
                                INSERT INTO sale_order_sync(sale_order_id,description,create_date,status,type,description_json,remote_ip_address) 
                                VALUES (
                                {sale_order.id}, '{json.dumps(data)}', '{now_plus_7_str}', 'pass', 'update', '{json.dumps(data)}'::json,'{remote_ip}'
                                ) 
                                """
                request.env.cr.execute(insert_log_sql)

                response = {
                    'status': 200,
                    'message': 'Updated Order',
                    'data': {
                        'order_id': sale_order.id
                    }
                }
                return response
            except Exception as e:
                e_str = e.args[0].replace("'", "") if e.args else ''
                insert_log_sql = f"""
                INSERT INTO sale_order_sync(sale_order_id,description,create_date,status,type,description_json,remote_ip_address,response) 
                VALUES (
                null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', 'update', '{json.dumps(data)}'::json, '{remote_ip}', '{e}'
                ) 
                """
                request.env.cr.execute(insert_log_sql)
                response = {
                    'status': 400,
                    'message': f'{e.__class__.__name__}: {e_str}',
                }
                return response

    @route("/api/sale_orders/tracking_delivery", methods=["POST"], type="json", auth="public", cors="*")
    def action_create_tracking_sale_order(self, **kwargs):
        Orders = request.env['sale.order']
        Items = request.env['sale.order.line']
        DeliverLevels = request.env['tracking.sale.order.deliver.status.config']
        now = datetime.now()
        now_plus_7_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        data = request.get_json_data()
        remote_ip = request.httprequest.environ['REMOTE_ADDR']
        reference_number = data.get('ReferenceNumber')
        verified = self.verify_webhook()
        if not verified:
            response = {
                'status': 404,
                'message': 'Not Found',
            }
            return response
        else:
            try:
                order_id_fix = reference_number
                sale_orders = Orders.sudo().search([('order_id_fix', '=', order_id_fix)])
                if not sale_orders:
                    response = {
                        'status': 400,
                        'message': 'Order not found',
                    }
                    insert_log_sql = f"""
                    INSERT INTO tracking_sale_order_delivery_sync(sale_order_id,description,create_date,status,response,description_json,remote_ip_address) 
                    VALUES (
                    null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', 'Order not found', '{json.dumps(data)}'::json, '{remote_ip}'
                    ) 
                    """
                    request.env.cr.execute(insert_log_sql)
                    return response
                else:
                    prevent_levels_str = request.env['ir.config_parameter'].sudo().get_param(
                        'prevent.update.deliver.status.level')
                    if not prevent_levels_str:
                        level_codes = []
                    else:
                        level_codes = [code.strip() for code in prevent_levels_str.split(',')]
                    items = sale_orders.order_line.filtered(lambda item: item.sublevel_id.level not in level_codes)
                    if items:
                        item_ids_str = ','.join([str(item_id) for item_id in items.ids])

                        tracking_number = data.get('TrackingNumber')
                        link_pdf = data.get('LinkPdf')
                        status = data.get('Status')
                        status_change_time = data.get('StatusChangeTime')

                        new_level_config = False
                        if status is not None:
                            new_level_config = DeliverLevels.sudo().search([('status', '=', status.lower())], limit=1)

                        update_item_tracking_sql = f"""
                        update sale_order_line
                        set 
                        """
                        if status is not None:
                            update_item_tracking_sql += f"""
                            deliver_status = '{status}',
                            """
                        else:
                            update_item_tracking_sql += f"""
                            deliver_status = null,
                            """

                        if status_change_time is not None:
                            update_item_tracking_sql += f"""
                            deliver_update_date = '{status_change_time}',
                            """
                        else:
                            update_item_tracking_sql += f"""
                            deliver_update_date = null,  
                        """

                        if not new_level_config:
                            update_item_tracking_sql += f"""
                            sublevel_id = null
                            """
                        else:
                            update_item_tracking_sql += f"""
                            sublevel_id = {new_level_config.level_id.id}
                            """
                            if new_level_config.level_id.level == 'L6.1' and status_change_time is not None:
                                update_item_tracking_sql += f"""
                                , deliver_date = '{status_change_time}'
                                """

                        update_item_tracking_sql += f"""
                        where id in ({item_ids_str})
                        """

                        request.env.cr.execute(update_item_tracking_sql)

                    insert_log_sql = f"""
                                                    INSERT INTO tracking_sale_order_delivery_sync(sale_order_id,description,create_date,status,description_json,remote_ip_address) 
                                                    VALUES (
                                                    null, '{json.dumps(data)}', '{now_plus_7_str}', 'pass', '{json.dumps(data)}'::json,'{remote_ip}'
                                                    ) 
                                                    """
                    request.env.cr.execute(insert_log_sql)
                    response = {
                        'status': 200,
                        'message': 'Updated Tracking Order Delivery Status',
                        'data': {
                            'reference_number': reference_number
                        }
                    }
                    return response
            except Exception as e:
                e_str = e.args[0].replace("'", "") if e.args else ''
                insert_log_sql = f"""
                                INSERT INTO tracking_sale_order_delivery_sync(sale_order_id,description,create_date,status,description_json,remote_ip_address,response) 
                                VALUES (
                                null, '{json.dumps(data)}', '{now_plus_7_str}', 'fail', '{json.dumps(data)}'::json, '{remote_ip}', '{e}'
                                ) 
                                """
                request.env.cr.execute(insert_log_sql)
                response = {
                    'status': 400,
                    'message': f'{e.__class__.__name__}: {e_str}',
                }
                return response
