# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import base64
import json
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sale.order.line']

    @api.constrains('production_id')
    def _check_production_id(self):
        for record in self:
            production_id = record.production_id
            if production_id:
                duplicate_code = self.sudo().search(
                    [('id', '!=', record.id), ('production_id', '=', production_id)])
                if duplicate_code:
                    raise ValidationError(f"This Production ID {production_id} already exists.")

    @api.model
    def default_get(self, fields_list):
        values = super(SaleOrderLine, self).default_get(fields_list)
        level = self.get_default_level()
        values['sublevel_id'] = level.id
        return values

    def get_default_level(self):
        payment_status = self.order_id.payment_status
        level_code = 'L1.1' if payment_status else 'L1'
        level = self.env['sale.order.line.level'].sudo().search([('level', '=', level_code)], limit=1)
        return level

    def default_sublevel_id(self):
        level = self.get_default_level()
        return level.id

    def _sublevel_domain(self):
        level = self.level_id
        return [('parent_id', '=', level.id)]

    image_ids = fields.Many2many('ir.attachment', string='Images')
    crosify_created_date = fields.Datetime(string='Create Date', default=fields.Datetime.now())
    crosify_create_by = fields.Char(string='MyAdmin Created By')
    product_sku = fields.Char(string='SKU', related='product_id.default_code', store=True, index=True)
    my_admin_order_id = fields.Char(string='Order ID', related='order_id.myadmin_order_id', store=True, index=True)
    my_admin_detailed_id = fields.Integer(string='My Admin Detailed ID', store=True, index=True)
    myadmin_product_id = fields.Integer(string='My Admin Product ID')
    order_id_fix = fields.Char(string='Order ID Fix', related='order_id.order_id_fix', store=True, index=True)
    product_name = fields.Char(string='Product Name', related='product_id.name', store=1)
    product_vendor_id = fields.Many2one('res.partner', string='Product Vendor')
    item_size = fields.Char(string='Item Size')
    description_item_size = fields.Char(string='Description Item Size')
    color_item = fields.Char(string='Color Item')
    box_size = fields.Char(string='Box Size')
    personalize = fields.Char(string='Personalize', tracking=1)
    package_size = fields.Char(string='Package Size')
    product_code = fields.Char(string='Product Code')
    product_type = fields.Char(string='Product Type', related='product_id.product_tmpl_product_type', store=True,
                               index=True)
    color_set_name = fields.Char(string='Color Set Name')
    design_serial_number = fields.Char(string='Design Serial Number')
    accessory_name = fields.Char(string='Accessory Name')
    base_cost = fields.Float(string='Base Cost')
    shipping_cost = fields.Float(string='Shipping Cost')
    logistic_cost = fields.Float(string='Logistic Cost')
    customer_note = fields.Text(string='Customer Note')
    priority = fields.Boolean(string='Priority', tracking=1)
    element_message = fields.Text(string='Element Message')
    extra_info = fields.Text(string='Extra Info')
    extra_service = fields.Char(string='Extra Service')
    status = fields.Char(string='Status')
    tips = fields.Float(string='Tips')
    channel_ref_id = fields.Char(string='Reference ID')
    # Fulfillment
    operator_id = fields.Many2one('hr.employee', string='Operator')
    hs_code = fields.Char(string='HS Code')
    tkn_code = fields.Char(string='TKN Code')
    tkn_url = fields.Char(string='TKN URL')
    label_file = fields.Binary(string='Label File')
    label_file_store_name = fields.Char(string='Label File Store Name')
    label_file_url = fields.Text(string="Label File Url")
    upload_tkn_date = fields.Datetime(string='Upload TKN Date')
    upload_tkn_by = fields.Many2one('hr.employee', string='Upload TKN By')
    is_upload_tkn = fields.Boolean(string='Is Upload TKN')
    note_fulfill = fields.Text(string='Fulfill Note')
    fulfill_order_employee_id = fields.Many2one('hr.employee', string='Fulfill Order By', index=True)
    fulfill_order_date = fields.Datetime(string='Fulfill Order Date')

    # fulfill vendor
    fulfill_vendor_date = fields.Datetime(string='Fulfill Vendor Date')
    fulfill_vendor_employee_id = fields.Many2one('hr.employee', string='Fulfill Vendor By', index=True)

    # Design
    designer_id = fields.Many2one('hr.employee', string='Designer', tracking=1)
    design_file_url = fields.Text(string='Design File', tracking=1)
    design_file_name = fields.Text(string='Design File Name')
    design_date = fields.Datetime(string='Design Date', tracking=1)
    variant = fields.Text(string='Variant')
    design_note = fields.Text(string='Design note', tracking=1)
    # tab production
    production_id = fields.Char(string='Production ID', tracking=1, index=True, copy=False)
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
    # Tab Shipping & Pickup
    address_sheft_id = fields.Many2one('fulfill.shelf', string='Address Sheft')
    shipping_date = fields.Datetime(string='Shipping Date')
    shipping_confirm_date = fields.Date(string='Shipping Confirm Date')
    packed_date = fields.Datetime(string='Packed Date')
    pickup_date = fields.Datetime(string='Pickup Date')
    deliver_date = fields.Datetime(string='Deliver Date')
    deliver_update_date = fields.Datetime(string='Deliver Update Date')
    deliver_status = fields.Char(string='Deliver Status')
    customer_received = fields.Boolean(string='Customer Received')
    # Tab Other Info
    note_change_request = fields.Text(string='Note Change Request')
    cancel_date = fields.Datetime(string='Cancel Date')
    cancel_reason_id = fields.Many2one('fulfill.cancel.item', string='Cancel Reason')
    cancel_note = fields.Text(string='Cancel Note')
    dispute_status = fields.Char(string='Dispute Status')
    dispute_note = fields.Text(string='Dispute Note')
    approve_by = fields.Many2one('hr.employee', string='Approve By')

    level_id = fields.Many2one('sale.order.line.level', domain=[('is_parent', '=', True)], string='Parent Level')
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', default=default_sublevel_id,
                                  domain=_sublevel_domain, tracking=1)
    last_update_level_date = fields.Datetime(string='Last Update Level')
    meta_field = fields.Text(string='Meta Field')
    crosify_discount_amount = fields.Float(string='Discount Amount')
    total_tax = fields.Float(string='Total Tax')
    cost_amount = fields.Float(string='Cost Amount')
    amount = fields.Float(string='Amount')
    variant = fields.Text(string='Variant')
    taxed_total_amount = fields.Float(string='Taxed Total Amount')
    crosify_approve_cancel_employee_id = fields.Many2one('hr.employee', string='Approve Cancel By')
    update_date = fields.Datetime(string='MyAdmin Update Date')
    update_by = fields.Char(string='MyAdmin Update By')
    chars = fields.Char(string='Chars')
    create_date = fields.Datetime(string='System Creation Date')
    name = fields.Char(string='Name')
    barcode_file = fields.Binary(string='Item Barcode')
    barcode_name = fields.Char(string='Barcode Name')
    error_type_id = fields.Many2one('fulfill.error', string='Error Type')
    error_note = fields.Text(string='Error Note')
    hs_code = fields.Char(string='HS Code', related='product_template_id.categ_id.hs_code', store=True, index=1)
    is_combo = fields.Boolean(string='Combo', default=False)
    production_line_id = fields.Many2one('item.production.line', string='Production Line')
    order_index = fields.Integer(string='Order Index', index=True)
    number_rp = fields.Integer('Number RP', default=0)
    is_create_so_rp = fields.Boolean('Is create SO Rp', default=False, copy=False)
    product_id = fields.Many2one(string='SKU', tracking=1)

    # override_fields
    price_unit = fields.Float(
        string="Unit Price",
        compute=False,
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=False)

    price_total = fields.Float(
        string="Total",
        compute='_compute_amount_custom',
        store=True, precompute=True)

    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount_custom',
        store=True, precompute=True)

    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount_custom',
        store=True, precompute=True)

    #variant product field
    color = fields.Char(string="Color", compute='compute_attribute_product', store=True)
    size = fields.Char(string="Size", compute='compute_attribute_product', store=True)
    other_option = fields.Char(string="Other option", compute='compute_attribute_product', store=True)

    qc_passed_date = fields.Datetime(string='QC Passed Date', tracking=1)

    def write(self, vals):
        # OVERRIDE
        sublevel_id = vals.get('sublevel_id')
        old_sublevel_id = self.sublevel_id
        if sublevel_id:
            level = self.env['sale.order.line.level'].sudo().browse(sublevel_id)
            if self.sublevel_id.level == 'L0' and level.level not in ['L1.1', 'L7.2']:
                raise ValidationError(_('Level must be Paid Order or Cancel / Refund'))
        res = super().write(vals)

        #set add_or_minus_fulfill_shelf
        if sublevel_id:
            new_sublevel_id = self.sublevel_id
            self.add_or_minus_fulfill_shelf(old_sublevel_id, new_sublevel_id)

        return res

    @api.depends('price_unit', 'crosify_discount_amount', 'total_tax')
    def _compute_amount_custom(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([
                line._convert_to_tax_base_line_dict()
            ])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': line.price_unit + line.total_tax - line.crosify_discount_amount,
            })

    def update_item_level_based_on_payment_status(self):
        for rec in self:
            payment_status = rec.order_id.payment_status
            level_code = 'L1.1' if payment_status else 'L1'
            sublevel = self.env['sale.order.line.level'].sudo().search([('level', '=', level_code)], limit=1)
            level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L1')], limit=1)
            item_sublevel = rec.sublevel_id
            if not item_sublevel or item_sublevel.level.strip() == 'L1' or item_sublevel.level.strip() == 'L1.1':
                rec.sublevel_id = sublevel.id
            rec.level_id = level.id

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrderLine, self).create(vals_list)
        res.update_item_level_based_on_payment_status()
        return res

    @api.model
    def action_change_state_awaiting_fulfill(self):
        itemLevels = self.env['sale.order.line.level'].sudo()
        safety_state_levels = [False, 'L1.1']
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().browse(item_ids)

        if any(item.sublevel_id.level not in safety_state_levels for item in items):
            raise ValidationError('There is an item with a different status than Paid Order')
        awaiting_fulfill_level = itemLevels.search([('level', '=', 'L2.1')], limit=1)
        parent_level = awaiting_fulfill_level.parent_id.id if awaiting_fulfill_level else False
        if not awaiting_fulfill_level:
            raise ValidationError('There is no state with level L2.1')
        if not parent_level:
            raise ValidationError('This Level does not have Parent Level')

        item_ids_sql = ','.join([str(item_id) for item_id in item_ids])

        update_state_items_sql = f"""
        UPDATE sale_order_line 
        SET sublevel_id = {awaiting_fulfill_level.id}, 
            level_id = {parent_level}
        WHERE 
        """
        if len(item_ids) > 1:
            update_state_items_sql += f"""
            id in ({item_ids_sql})
            """
        else:
            update_state_items_sql += f"""
                        id = {item_ids_sql}
                        """
        self.env.cr.execute(update_state_items_sql)

    @api.model
    def action_create_item_production_id(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        not_order_id_items = items.filtered(lambda item: not item.my_admin_order_id)
        if not_order_id_items:
            no_order_id_order_ids = ','.join([str(item.order_id_fix) for item in not_order_id_items])
            raise ValidationError(f'Items with no Order ID: {no_order_id_order_ids}')
        had_production_id_items = items.filtered(lambda item: item.production_id)
        if had_production_id_items:
            had_production_id_items_order_ids = ','.join([str(item.order_id_fix) for item in had_production_id_items])
            raise ValidationError(f'Item already has Production ID: {had_production_id_items_order_ids}')
        order_id_fixes = list(set(items.mapped('order_id_fix')))
        for order_id_fix in order_id_fixes:
            self.with_delay(description=f'Action Create Production ID For Order ID Fix = {order_id_fix}',
                            channel="root.channel_sale_order_line").action_create_production_id_cron(order_id_fix,
                                                                                                     items)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Creating Production ID"),

                'type': 'warning',
                'message': _("System is creating Production ID"),

                'sticky': True,
            },
        }

    @api.model
    def action_create_sale_order_qc_failed(self):

        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        qc_failed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.4')], limit=1)
        if not qc_failed_level:
            raise UserError(_("Not found level! Please contact admin."))
        items_has_level_diff_qc_fail = items.filtered(lambda item: item.sublevel_id.id != qc_failed_level.id)

        if items_has_level_diff_qc_fail:
            raise UserError(_("Items selected is not level QC Failed ."))
        qc_failed_items = items.filtered(lambda item: item.sublevel_id.id == qc_failed_level.id)

        filter_items = qc_failed_items.filtered(lambda item: not item.error_type_id
                                                             or not item.error_type_id.level_back_id
                                                             or item.is_create_so_rp
                                                )

        for filter_item in filter_items:
            if not filter_item.error_type_id:
                raise UserError("Error Type does not exist in Item %s!" % filter_item.display_name)

            if not filter_item.error_type_id.level_back_id:
                raise UserError(
                    "Level back does not exist in Error Type: %s!" % filter_item.error_type_id.error_type)

            if filter_item.is_create_so_rp:
                raise UserError("You cannot create an order that has already created (Order QC Failed).")
        try:
            order_created = {}
            for qc_failed_item in qc_failed_items:

                qc_failed_item.is_create_so_rp = True

                if not order_created.get(qc_failed_item.order_id.order_id_fix):

                    post_order_id = self.handle_name_myadmin_order_id(qc_failed_item.order_id.myadmin_order_id,
                                                                      qc_failed_item.number_rp)

                    add_value = {
                        'myadmin_order_id': post_order_id,
                        'order_line': False,
                        'original_order_id': qc_failed_item.order_id.id
                        }
                    new_sale_order_id = qc_failed_item.order_id.copy(add_value).id

                    order_created.update({
                        qc_failed_item.order_id.order_id_fix: new_sale_order_id
                    })
                else:
                    new_sale_order_id = order_created.get(qc_failed_item.order_id.order_id_fix)
                fulfill_error_id = qc_failed_item.error_type_id

                value_order_line = {
                    'order_id': new_sale_order_id,
                    'sublevel_id': qc_failed_item.error_type_id.level_back_id.id,
                    'number_rp': qc_failed_item.number_rp + 1
                }
                # ignore fields
                fields_ignores = fulfill_error_id.fields_ignore_ids
                for line in fields_ignores:
                    value_order_line[line.name] = False

                qc_failed_item_id = qc_failed_item.copy(value_order_line)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Creating Sale Order"),

                    'type': 'success',
                    'message': _("System is creating Sale Order."),
                },
            }
        except Exception as e:
            _logger.exception(str(e))
            raise UserError("Something went wrong, please contact admin!")

    def handle_name_myadmin_order_id(self, myadmin_order_id, number_rp):

        if number_rp:
            # Tìm vị trí của chuỗi "Rp"
            rp_index = myadmin_order_id.find("RP")
            # Kiểm tra xem chuỗi "Rp" có tồn tại trong chuỗi không
            if rp_index != -1:
                # Nếu tồn tại, cắt chuỗi từ đầu đến vị trí "Rp"
                result_str = myadmin_order_id[:rp_index + len("RP")]
            else:
                result_str = ''

            return result_str + '-' + str(number_rp)

        else:
            return myadmin_order_id + '-RP'



    def action_create_production_id_cron(self, order_id_fix, items):
        total_items = self.sudo().search([('order_id_fix', '=', order_id_fix)])
        none_production_id_items = total_items.filtered(lambda item: not item.production_id)
        selected_items = items.filtered(lambda item: item.order_id_fix == order_id_fix)
        has_production_id_items = total_items.filtered(lambda item: item.production_id).mapped('production_id')
        if has_production_id_items:
            list_index = [int(rec.split('-')[1]) for rec in has_production_id_items if len(rec.split('-')) > 1]
            max_index = max(list_index) if len(list_index) > 0 else 0
        else:
            max_index = 0
        for index, item in enumerate(none_production_id_items):
            if item.id in selected_items.ids:
                if item.order_index > 0:
                    production_id = f'{item.order_id_fix}-{item.order_index}'
                else:
                    if len(total_items) > 1:
                        production_id = f'{item.order_id_fix}-{max_index + index + 1}'
                    else:
                        production_id = f'{item.order_id_fix}'
                item.production_id = production_id

    @api.model
    def action_update_order_fulfill(self):
        item_ids = self._context.get('active_ids', [])
        current_employee_id = self.env.user.employee_id
        fulfilled_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L2.2')], limit=1)
        if not fulfilled_level:
            raise ValidationError(_('There is no Fulfilled Level'))
        items = self.env['sale.order.line'].sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(item.sublevel_id.level != 'L2.1' for item in items):
            raise ValidationError('There is an Item with a different status than Awaiting Fulfillment ')
        for item in items:
            item.with_delay(
                description=f'Action Update Fulfillment Order For Item With Production ID = {item.production_id}',
                channel='root.channel_sale_order_line').action_cron_update_order_fulfill(
                fulfilled_level, current_employee_id)

    def action_cron_update_order_fulfill(self, fulfilled_level, current_employee_id):
        self.write({
            'sublevel_id': fulfilled_level.id,
            'level_id': fulfilled_level.parent_id.id,
            'fulfill_order_date': datetime.now(),
            'fulfill_order_employee_id': current_employee_id.id
        })

    @api.model
    def action_update_vendor_fulfill(self):
        item_ids = self._context.get('active_ids', [])
        items = self.env['sale.order.line'].sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(item.sublevel_id.level != 'L3.2' for item in items):
            raise ValidationError('There is an Item with a different status than Designed')
        return {
            "type": "ir.actions.act_window",
            "res_model": "update.fulfillment.wizard",
            "context": {},
            "name": "Update Vendor Fulfillment",
            'view_mode': 'form',
            "target": "new",
        }

    def action_cron_action_update_fulfill_vendor(self, wizard_id, employee_id, fulfilled_vendor_level):
        item = self
        item_fields_mapping = {
            'production_vendor_id': 'product_vendor_id',
            'packaging_vendor_id': 'packaging_vendor_id',
            'shipping_vendor_id': 'shipping_vendor_id',
        }
        update_type = wizard_id.update_type

        if update_type == 'default':
            product_type_fulfill_data = self.env['sale.order.product.type.fulfill'].sudo().search(
                [('product_type_id', '=', item.product_id.product_tmpl_id.id)], limit=1)
            if product_type_fulfill_data:
                for field in item_fields_mapping:
                    item[field] = product_type_fulfill_data[item_fields_mapping[field]].id
        else:
            for field in item_fields_mapping:
                item[field] = wizard_id[field].id

        item.write({
            'fulfill_vendor_employee_id': employee_id,
            'fulfill_vendor_date': datetime.now(),
            'sublevel_id': fulfilled_vendor_level.id,
        })

    @api.model
    def action_creating_shipment_for_item_model(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        fulfill_vedor_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.0')], limit=1)
        if not fulfill_vedor_level:
            raise ValidationError(_('There is no Fulfill Vendor Level'))
        not_available_items = items.filtered(lambda item: item.sublevel_id.sequence < fulfill_vedor_level.sequence)
        if not_available_items:
            not_available_orders_name = list(set(not_available_items.mapped('order_id').mapped('order_id_fix')))
            not_available_orders_name_str = ','.join([name for name in not_available_orders_name])
            raise ValidationError(_(f'Not Available Items With Order ID FIX: {not_available_orders_name_str}'))
        items.action_creating_shipment_for_item()

    def action_creating_shipment_for_item(self):
        Orders = self.env['sale.order'].sudo()
        order_id_fixes = list(set(self.mapped('order_id_fix')))
        for order_id_fix in order_id_fixes:
            order = Orders.search([('order_id_fix', '=', order_id_fix), ('is_upload_tkn', '=', False)], limit=1)
            if order:
                data = order.get_label_json_data()
                order.with_delay(description=data).action_creating_shipment_for_order()

    def action_updated_shipping_items(self, order):
        items = self
        updated_items = items.filtered(lambda item: item.order_id.id == order.id)
        response = order.get_label_data()
        if response.status_code == 200:
            total_data = json.loads(response.text)
            data = total_data.get('labels')[0]
            if not data.get('linkPdf'):
                raise ValidationError(total_data.get('msg'))
            current_employee = self.env.user.employee_id
            sub_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L2.3')], limit=1)
            if not sub_level:
                raise ValidationError('There is no state with level Creating Shipment')
            for rec in updated_items:
                rec.write({
                    'label_file_url': data.get('linkPdf'),
                    'tkn_code': data.get('shipmentId'),
                    'is_upload_tkn': True,
                    'upload_tkn_date': fields.Datetime.now(),
                    'upload_tkn_by': current_employee.id,
                    'sublevel_id': sub_level.id,
                    'level_id': sub_level.parent_id.id,
                })
        else:
            raise ValidationError(response.reason)

    def action_creating_shipment_for_item_order(self):
        current_employee = self.env.user.employee_id
        # sub_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L2.3')], limit=1)
        # if not sub_level:
        #     raise ValidationError('There is no state with level Creating Shipment')
        for rec in self:
            order_id = rec.order_id
            rec.write({
                'label_file_url': order_id.label_file_url,
                'tkn_code': order_id.tkn,
                'is_upload_tkn': True,
                'upload_tkn_date': fields.Datetime.now(),
                'upload_tkn_by': current_employee.id,
            })

    @api.model
    def action_set_awaiting_design_level(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(item.sublevel_id.level != 'L2.2' for item in items):
            raise ValidationError('There is an Item with a different status than Fulfilled')
        awaiting_design_sub_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L3.1')], limit=1)
        if not awaiting_design_sub_level:
            raise ValidationError('There is no state with level Awaiting Design')
        for item in items:
            item.with_delay(
                description=f'Action Update Awaiting Design Level For Item With Production ID = {item.production_id}',
                channel='root.channel_sale_order_line').action_cron_set_awaiting_design_level(awaiting_design_sub_level)

    def action_cron_set_awaiting_design_level(self, awaiting_design_sub_level):
        self.write({
            'sublevel_id': awaiting_design_sub_level.id,
            'level_id': awaiting_design_sub_level.parent_id.id,
        })

    @api.model
    def action_update_level(self):
        item_ids = self._context.get('active_ids', [])
        return {
            "type": "ir.actions.act_window",
            "res_model": "update.item.level.wizard",
            "context": {
                'default_item_ids': [(6, 0, item_ids)],
            },
            "name": "Update Items Level",
            'view_mode': 'form',
            "target": "new",
        }

    @api.model
    def action_set_designer(self):
        item_ids = self._context.get('active_ids', [])
        return {
            "type": "ir.actions.act_window",
            "res_model": "update.designer.wizard",
            "context": {
                'default_item_ids': [(6, 0, item_ids)],
            },
            "name": "Update Designer",
            'view_mode': 'form',
            "target": "new",
        }

    @api.model
    def action_set_design_note(self):
        item_ids = self._context.get('active_ids', [])
        return {
            "type": "ir.actions.act_window",
            "res_model": "update.design.note.wizard",
            "context": {
                'default_item_ids': [(6, 0, item_ids)],
            },
            "name": "Update Design Note",
            'view_mode': 'form',
            "target": "new",
        }

    @api.model
    def action_create_production_for_item(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(item.sublevel_id.level != 'L4.0' for item in items):
            raise ValidationError('There is an Item with a different status than Fulfill Vendor')
        return {
            "type": "ir.actions.act_window",
            "res_model": "mo.production",
            "context": {
                'default_date': fields.Date.today(),
                'default_employee_id': self.env.user.employee_id.id,
                'default_mo_production_line_ids': [(6, 0, item_ids)],
            },
            "name": "Production",
            'view_mode': 'form',
            "target": "current",
        }

    @api.model
    def action_action_cancel_item(self):
        item_ids = self._context.get('active_ids', [])
        return {
            "type": "ir.actions.act_window",
            "res_model": "cancel.item.wizard",
            "context": {
                "default_item_ids": [(6, 0, item_ids)]
            },
            "name": "Cancel Item",
            'view_mode': 'form',
            "target": "new",
        }

    @api.model
    def action_update_item_design_info(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(item.sublevel_id.level != 'L3.1' for item in items):
            raise ValidationError('There is an Item with a different status than Awaiting Design')
        wizard = self.env['update.item.design.wizard'].sudo().create({
            'sale_order_line_ids': [(6, 0, item_ids)]
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "update.item.design.wizard",
            "context": {
                "create": 0
            },
            "res_id": wizard.id,
            "name": "Update Design File",
            'view_mode': 'form',
            "target": "current",
        }

    @api.depends('order_partner_id', 'order_id', 'product_id')
    def _compute_display_name(self):
        for so_line in self.sudo():
            name = '{} - {}'.format(so_line.order_id.name,
                                    so_line.name and so_line.name.split('\n')[0] or so_line.product_id.name)
            if so_line.production_id:
                name = f'{name} - {so_line.production_id}'
            so_line.display_name = name

    @api.model
    def action_generate_item_barcode_server(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(not item.production_id for item in items):
            raise ValidationError('Could not generate barcode for None Production ID Item')
        return items.action_generate_item_barcode()

    def action_generate_item_barcode(self):
        try:
            total_items = len(self)
            item_pairs_number = total_items // 2 + total_items % 2

            data = []
            for pair in range(item_pairs_number):
                start_index = pair * 2
                end_index = start_index + 2
                pair_datas = []
                for rec in self[start_index:end_index]:
                    order_total_items = self.sudo().search([('order_id_fix', '=', rec.order_id_fix), ('is_create_so_rp', '=', False)])
                    total_product_types = list(set(order_total_items.mapped('product_type')))
                    product_str = f'{rec.address_sheft_id.shelf_code}'
                    for product_type in total_product_types:
                        product_type_items = order_total_items.filtered(lambda item: item.product_type == product_type)
                        product_format = f'_{len(product_type_items)}{product_type}'
                        product_str += product_format
                    shipping_vendor = rec.shipping_vendor_id.ref if rec.shipping_vendor_id and rec.shipping_vendor_id.ref else ''
                    seller_id = rec.order_id.seller_id
                    if seller_id:
                        seller_code = '' if not seller_id.code else seller_id.code
                        seller_name = '' if not seller_id.name else seller_id.name
                        seller = f'{seller_code} {seller_name}'
                    else:
                        seller = ''

                    size = [attribute.product_attribute_value_id.name for attribute in
                                 rec.product_id.product_template_attribute_value_ids if
                                 attribute.attribute_id.name in ['Size']]
                    color = [attribute.product_attribute_value_id.name for attribute in
                                  rec.product_id.product_template_attribute_value_ids if
                                  attribute.attribute_id.name in ['Color']]
                    other_option = [attribute.product_attribute_value_id.name for attribute in
                                         rec.product_id.product_template_attribute_value_ids if
                                         attribute.attribute_id.name in ['Other Option']]

                    pair_datas.append({
                        'production_id': rec.production_id,
                        'order_id_name': rec.order_id_fix,
                        'product_type': rec.product_type,
                        'shipping_vendor': shipping_vendor,
                        'seller': seller,
                        'personalize': rec.personalize[:80] if rec.personalize else '',
                        'shelf_code': rec.address_sheft_id.shelf_code,
                        'production_vendor_code': rec.production_vendor_id.ref if rec.production_vendor_id and rec.production_vendor_id.ref else '',
                        'product_str': product_str,
                        'size': size[0] if len(size) > 0 else '',
                        'color': color[0] if len(color) > 0 else '',
                        'other_option': other_option[0] if len(other_option) > 0 else '',

                    })
                data.append(pair_datas)
            item_data = {
                'items_data': data
            }
            report = self.env.ref('crosify_order.action_generate_item_barcode')
            report_action = report.report_action(self, data=item_data, config=False)
            report_action.update({'close_on_report_download': True})
            return report_action

        except (ValueError, AttributeError):
            raise ValidationError('Cannot convert into barcode.')

    @api.model
    def action_set_address_shelf(self):
        item_ids = self._context.get('active_ids', [])
        self.with_delay(channel='root.sale').queue_action_set_address_shelf(item_ids)

    def queue_action_set_address_shelf(self, item_ids):
        try:
            items = self.sudo().search([('id', 'in', item_ids)], order='product_type,order_id').filtered(lambda item: not item.address_sheft_id)
            data_shelf = {}
            for item in items:
                if not item.address_sheft_id and item.product_type:
                    order_id = item.order_id
                    product_type = item.product_type

                    value_current_shelf = self.handle_data_shelf(data_shelf, order_id, product_type)
                    if value_current_shelf:
                        fulfill_shelf_id = value_current_shelf
                    else:
                        key_shelf = str(order_id) + str(product_type)
                        fulfill_shelf_id = item.search_fulfill_shelf(item.product_type)
                        data_shelf[key_shelf] = fulfill_shelf_id

                    if fulfill_shelf_id:
                        item.write({
                            'address_sheft_id': fulfill_shelf_id,
                        })
                        fulfill_shelf_obj = self.env['fulfill.shelf'].browse(fulfill_shelf_id)
                        fulfill_shelf_obj.write({
                            'temp_shelf': fulfill_shelf_obj.temp_shelf + 1,
                        })


        except Exception as e:
            _logger.exception(str(e))
            raise UserError("Something went wrong! Please contact the administrator.")

    def search_fulfill_shelf(self, product_type):
        """
        Search for product.type.shelf.type and fulfill.shelf and return fulfill.shelf.id match
        """
        product_type_shelf_type = self.env['product.type.shelf.type'].sudo().search(
            [('product_type', '=', product_type)], limit=1)
        if product_type_shelf_type and product_type_shelf_type.shelf_type_id:
            shelf_type_id = product_type_shelf_type.shelf_type_id.id
            fulfill_shelf_ids = self.env['fulfill.shelf'].sudo().search([
                ('shelf_type', '=', shelf_type_id), ('available', '=', True)])
            fulfill_shelf_id = self.get_min_temp_shelf_fulfill_shelf(fulfill_shelf_ids)

            if fulfill_shelf_id:
                return fulfill_shelf_id.id
            return False
        return False

    def get_min_temp_shelf_fulfill_shelf(self, fulfill_shelf_ids):
        if fulfill_shelf_ids:
            fulfill_shelf_id = fulfill_shelf_ids[0]
        else:
            return False
        for line in fulfill_shelf_ids:
            if fulfill_shelf_id.temp_shelf > line.temp_shelf:
                fulfill_shelf_id = line
        return fulfill_shelf_id

    def handle_data_shelf(self, data_shelf, order_id, product_type):

        key_shelf = str(order_id) + str(product_type)
        if data_shelf.get(key_shelf):
            return data_shelf.get(key_shelf)
        else:
            return False

    def add_or_minus_fulfill_shelf(self, old_sublevel_id, new_sublevel_id):

        config_set_line_level_id = self.env['config.set.line.level'].sudo().search([('type', '=', 'shelf')], limit=1)

        if config_set_line_level_id:
            set_shelf_ids = config_set_line_level_id.set_shelf_ids.ids
            pre_set_shelf_ids = config_set_line_level_id.pre_set_shelf_ids.ids
            post_set_shelf_ids = config_set_line_level_id.post_set_shelf_ids.ids
        else:
            set_shelf_ids = []
            pre_set_shelf_ids = []
            post_set_shelf_ids = []

        if new_sublevel_id and new_sublevel_id.id in set_shelf_ids:
            if self.address_sheft_id:
                self.address_sheft_id.current_shelf += 1

        if (old_sublevel_id and old_sublevel_id.id in set_shelf_ids
                and new_sublevel_id and new_sublevel_id.id in post_set_shelf_ids):
            if self.address_sheft_id:
                self.address_sheft_id.current_shelf -= 1
                self.address_sheft_id.temp_shelf -= 1

        if (old_sublevel_id and old_sublevel_id.id in post_set_shelf_ids
                and new_sublevel_id and new_sublevel_id.id in pre_set_shelf_ids):
            if self.address_sheft_id:
                self.address_sheft_id.temp_shelf += 1

        if (old_sublevel_id and old_sublevel_id.id in post_set_shelf_ids
                and new_sublevel_id and new_sublevel_id.id in set_shelf_ids):
            if self.address_sheft_id:
                self.address_sheft_id.temp_shelf += 1

    @api.depends('product_id.product_template_attribute_value_ids',
                 'product_id.product_template_attribute_value_ids.attribute_line_id.attribute_id.code')
    def compute_attribute_product(self):
        for rec in self:
            color = False
            size = False
            other_option = False

            if rec.product_id:
                attribute_ids = rec.product_id.product_template_attribute_value_ids

                for attribute in attribute_ids:
                    if attribute.attribute_line_id.attribute_id.code == 'color':
                        color = attribute.name
                    if attribute.attribute_line_id.attribute_id.code == 'size':
                        size = attribute.name
                    if attribute.attribute_line_id.attribute_id.code == 'other_option':
                        other_option = attribute.name

            rec.color = color
            rec.size = size
            rec.other_option = other_option

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        awaiting_design_tree = res['views']['list']['arch']
        if 'awaiting_design_tree' in awaiting_design_tree:
            res['views']['list']['arch'] = """
                <tree string="awaiting_design_tree" create="0" export_xlsx="0" js_class="button_in_tree">
                        <field name="production_id"/>
                        <field name="order_id_fix"/>
                        <field name="my_admin_order_id"/>
                        <field name="product_sku"/>
                        <field name="product_type"/>
                        <field name="color"/>
                        <field name="size"/>
                        <field name="other_option"/>
                        <field name="personalize"/>
                        <field name="designer_id"/>
                        <field name="design_note"/>
                        <field name="sublevel_id"/>
                    </tree>
            """
        return res
