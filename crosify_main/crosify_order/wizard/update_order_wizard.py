# -*- coding: utf-8 -*-
import pytz
import openpyxl
import base64
from io import BytesIO
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UpdateOrderWizard(models.TransientModel):
    _name = 'update.order.wizard'
    _rec_name = 'name'

    name = fields.Char(default='Update Order')
    item_file = fields.Binary(string='Items File')
    item_file_name = fields.Char(string='Items')
    line_ids = fields.One2many('update.order.line.wizard', 'update_order_wizard_id', string='Update Orders')

    def action_import_items(self):
        Items = self.env['sale.order.line'].sudo()
        Products = self.env['product.product'].sudo()
        ItemLines = self.env['update.order.line.wizard'].sudo()
        States = self.env['res.country.state'].sudo()
        Country = self.env['res.country'].sudo()
        import_file = self.item_file
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
                first_name = record[2]
                last_name = record[3]
                street = record[4]
                street2 = record[5]
                city = record[6]
                state_code = record[7]
                country_code = record[8]
                if not country_code:
                    country_id = False
                else:
                    state_id = Country.search([('code', '=', country_code)], limit=1).id
                if not state_code:
                    state_id = False
                else:
                    state_id = States.search([('code', '=', state_code), ('country_id', '=', country_id)], limit=1).id
                zip = record[9]
                phone = record[10]
                email = record[11]

                if not order_id_fix:
                    continue
                else:
                    order_id_fix = order_id_fix.strip()
                    order_id_fixes.append(order_id_fix)
                    order = Items.search([('order_id_fix', '=', order_id_fix)], limit=1)
                    if order:
                        item_file_datas.append({
                            'order_id_fix': order_id_fix,
                            'order_id': order.id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'street': street,
                            'street2': street2,
                            'city': city,
                            'state_id': state_id,
                            'country_id': country_id,
                            'zip': zip,
                            'phone': phone,
                            'email': email,
                        })

            item_ids = ItemLines.create(item_file_datas)
            self.line_ids = [(6, 0, item_ids.ids)]

        except:
            raise ValidationError(_('Insert Invalid File'))

    def action_update_item(self):
        line_ids = self.line_ids
        for line in line_ids:
            order_id = line.order_id
            if order_id and order_id.partner_id:
                order_id.partner_id.write({
                    'first_name': line.first_name,
                    'last_name': line.last_name,
                    'street': line.street,
                    'street2': line.street2,
                    'city': line.city,
                    'state_id': line.state_id.id,
                    'country_id': line.country_id.id,
                    'zip': line.zip,
                    'phone': line.phone,
                    'email': line.email,
                })


class UpdateOrderLineWizard(models.TransientModel):
    _name = 'update.order.line.wizard'

    update_order_wizard_id = fields.Many2one('update.order.wizard')
    order_id_fix = fields.Char(string='Order ID Fix', required=True)
    order_id = fields.Many2one('sale.order', string='Order')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    street = fields.Char(string='Street 1')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='Zip Code')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
