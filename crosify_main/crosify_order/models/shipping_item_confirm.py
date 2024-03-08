from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import openpyxl
import base64
from io import BytesIO


class ShippingItemConfirm(models.Model):
    _name = 'shipping.item.confirm'
    _rec_name = 'code'

    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id.id,
                                  required=True, index=True)
    note = fields.Text(string='Note')
    item_ids = fields.One2many('shipping.item.confirm.line', 'shipping_item_confirm_id', 'Confirm Items')
    delivered_item_file = fields.Binary(string='Delivered Items File')
    delivered_item_file_name = fields.Char(string='Delivered')
    relate_pickup_ids = fields.Many2many('pickup.item', 'shipping_item_confirm_pickup_item_rel', 'shipping_item_confirm_id', 'pickup_id', string='Relate Pickup')
    pickup_order_ids = fields.One2many('shipping.item.confirm.pickup.order', 'shipping_item_confirm_id', string='Pickup Info', compute='compute_pickup_order_ids', store=True)
    pickup_order_error_ids = fields.One2many('shipping.item.confirm.pickup.order.error', 'shipping_item_confirm_id', string='Pickup Error Info', compute='compute_pickup_order_error_ids', store=True)

    @api.depends('pickup_order_ids', 'item_ids')
    def compute_pickup_order_error_ids(self):
        Errors = self.env['shipping.item.confirm.pickup.order.error'].sudo()
        for rec in self:
            items = rec.item_ids
            pickup_order_ids = rec.pickup_order_ids

            item_order_id_fix_list = set(items.mapped('order_id_fix'))
            pickup_order_order_id_fix_list = set(pickup_order_ids.mapped('order_id_fix'))

            diff = pickup_order_order_id_fix_list.difference(item_order_id_fix_list)
            error_items = pickup_order_ids.filtered(lambda line: line.order_id_fix in list(diff))
            datas = []
            for data in error_items:
                datas.append({
                    'shipping_item_confirm_id': rec.id,
                    'pickup_id': data.pickup_id.id,
                    'pickup_date': data.pickup_date,
                    'order_id_fix': data.order_id_fix,
                    'tkn_code': data.tkn_code,
                })
            errors = Errors.create(datas)
            rec.pickup_order_error_ids = [(6, 0, errors.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        results = super(ShippingItemConfirm, self).create(vals_list)
        for val in results:
            if not val.code:
                date = val.date
                time = date.strftime('%d/%m/%Y')
                today_format_split = time.split('/')
                date = today_format_split[0]
                month = today_format_split[1]
                year = today_format_split[-1][-2:]
                sequence = self.env['ir.sequence'].sudo().next_by_code('shipping.item.confirm') or ''
                code = f'CONFIRM_{date}{month}{year}_{sequence}'
                val.code = code
        return results

    @api.depends('relate_pickup_ids')
    def compute_pickup_order_ids(self):
        PickupOrders = self.env['shipping.item.confirm.pickup.order'].sudo()
        for rec in self:
            pickup_ids = rec.relate_pickup_ids
            datas = []
            for pickup in pickup_ids:
                total_items = pickup.item_ids
                order_lines_total = total_items.filtered(lambda line: line.type == 'order')
                orders = order_lines_total.order_ids
                for order in orders:
                    datas.append({
                        'pickup_id': pickup.id,
                        'pickup_date': pickup.date,
                        'order_id_fix': order.order_id_fix,
                        'tkn_code': order.tkn,
                    })
            pickup_orders = PickupOrders.create(datas)
            rec.pickup_order_ids = [(6, 0, pickup_orders.ids)]

    def action_import_items(self):
        Orders = self.env['sale.order'].sudo()
        ItemLines = self.env['shipping.item.confirm.line'].sudo()
        import_file = self.delivered_item_file
        try:
            wb = openpyxl.load_workbook(

                filename=BytesIO(base64.b64decode(import_file)), read_only=True
            )
            item_file_datas = []
            order_id_fixes = []
            ws = wb.active
            for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,
                                       max_col=None, values_only=True):
                order_id_fix = record[1]
                if order_id_fix and order_id_fix not in order_id_fixes:
                    order_id_fix = order_id_fix.strip()
                    order_id_fixes.append(order_id_fix)
                    order = Orders.search([('order_id_fix', '=', order_id_fix), ('tkn', '!=', False)], limit=1)
                    if order:
                        item_file_datas.append({
                            'order_id_fix': order_id_fix,
                            'tkn_code': order.tkn,
                            'shipping_item_confirm_id': self.id,
                        })

            item_ids = ItemLines.create(item_file_datas)
            self.item_ids = [(6, 0, item_ids.ids)]

        except:
            raise ValidationError(_('Insert Invalid File'))

    def action_confirm_item(self):
        Levels = self.env['sale.order.line.level'].sudo()
        Orders = self.env['sale.order'].sudo()
        ShippingLines = self.env['shipping.item.confirm.line'].sudo()
        pickup_level = Levels.search([('level', '=', 'L5.1')], limit=1)
        shipping_confirm_level = Levels.search([('level', '=', 'L5.2')], limit=1)
        if not pickup_level:
            raise ValidationError('There is no state with level Pickup')
        if not pickup_level:
            raise shipping_confirm_level('There is no state with level Shipping Confirm')

        if len(self.pickup_order_error_ids) > 0:
            # error_items = ShippingLines.search([('order_id_fix', 'in', list(diff))])
            # for error_item in error_items:
            #     error_item.is_fail_order = True
            raise ValidationError('Can not Confirm Item')
        else:
            order_id_fixes = self.item_ids.mapped('order_id_fix')
            orders = Orders.search([('order_id_fix', 'in', order_id_fixes)])
            pickup_items = orders.mapped('order_line').filtered(lambda item: item.sublevel_id.id == pickup_level.id)
            for item in pickup_items:
                item.write({
                    'sublevel_id': shipping_confirm_level.id,
                    'shipping_confirm_date': datetime.now().date(),
                })

class ShippingItemConfirmPickupOrder(models.Model):
    _name = 'shipping.item.confirm.pickup.order'

    shipping_item_confirm_id = fields.Many2one('shipping.item.confirm')
    pickup_id = fields.Many2one('pickup.item', string='Pickup Item')
    pickup_date = fields.Date(string='Pickup Date')
    order_id_fix = fields.Char(string='Order ID Fix')
    tkn_code = fields.Char(string='TKN Code')

class ShippingItemConfirmPickupOrderError(models.Model):
    _name = 'shipping.item.confirm.pickup.order.error'

    shipping_item_confirm_id = fields.Many2one('shipping.item.confirm')
    pickup_id = fields.Many2one('pickup.item', string='Pickup Item')
    pickup_date = fields.Date(string='Pickup Date')
    order_id_fix = fields.Char(string='Order ID Fix')
    tkn_code = fields.Char(string='TKN Code')


class ShippingItemConfirmLine(models.Model):
    _name = 'shipping.item.confirm.line'

    shipping_item_confirm_id = fields.Many2one('shipping.item.confirm')
    order_id_fix = fields.Char(string='Order ID Fix')
    tkn_code = fields.Char(string='TKN Code')

