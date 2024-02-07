# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sale.order.line']

    @api.constrains('production_id')
    def _check_production_id(self):
        for record in self:
            production_id = record.production_id

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
    crosify_created_date = fields.Date(string='MyAdmin Create Date')
    crosify_create_by = fields.Char(string='MyAdmin Created By')
    product_sku = fields.Char(string='SKU', related='product_id.default_code', store=True, index=True)
    my_admin_order_id = fields.Char(string='My Admin Order ID', related='order_id.myadmin_order_id', store=True, index=True)
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
    product_type = fields.Char(string='Product Type', related='product_id.product_tmpl_id.product_type', store=True, index=True)
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
    fulfill_employee_id = fields.Many2one('hr.employee', string='Fulfill By', index=True)

    #Design
    designer_id = fields.Many2one('hr.employee', string='Designer')
    design_file_url = fields.Text(string='Design File')
    design_file_name = fields.Text(string='Design File Name')
    design_date = fields.Date(string='Design Date')
    variant = fields.Text(string='Variant')
    #tab production
    production_id = fields.Char(string='Production ID', tracking=1)
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
    address_sheft_id = fields.Many2one('fulfill.shelf', string='Address Sheft')
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
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', default=default_sublevel_id, domain=_sublevel_domain, tracking=1)
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
        order_id_fixes = items.mapped('order_id_fix')
        for order_id_fix in order_id_fixes:
            total_items = self.sudo().search([('order_id_fix', '=', order_id_fix)])
            selected_items = items.filtered(lambda item: item.order_id_fix == order_id_fix)
            for index, item in enumerate(total_items):
                if item.id in selected_items.ids:
                    if len(total_items) > 1:
                        production_id = f'{item.order_id_fix}-{index+1}'
                    else:
                        production_id = f'{item.order_id_fix}'
                    item.production_id = production_id

    @api.model
    def action_update_fulfill(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(item.sublevel_id.level != 'L2.1' for item in items):
            raise ValidationError('There is an Item with a different status than Awaiting Fulfillment ')
        employee_id = self.env.user.employee_id.id
        for item in items:
            product_type_fulfill_data = self.env['sale.order.product.type.fulfill'].sudo().search([('product_type_id', '=', item.product_id.product_tmpl_id.id)], limit=1)
            if product_type_fulfill_data:
                fulfilled_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L2.2')], limit=1)
                if not fulfilled_level:
                    raise ValidationError('There is no status Fulfilled')
                item_fields_mapping = {
                    'production_vendor_id': 'product_vendor_id',
                    'packaging_vendor_id': 'packaging_vendor_id',
                    'shipping_vendor_id': 'shipping_vendor_id',
                }
                for field in item_fields_mapping:
                    if not item[field]:
                        item[field] = product_type_fulfill_data[item_fields_mapping[field]].id
                item.fulfill_employee_id = employee_id
                item.fulfill_date = datetime.now().date()
                item.sublevel_id = fulfilled_level.id












