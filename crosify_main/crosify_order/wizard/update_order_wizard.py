
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
    line_ids = fields.One2many('update.order.line.wizard', 'update_item_wizard_id', string='Update Orders')

    def action_import_items(self):
        Items = self.env['sale.order.line'].sudo()
        Products = self.env['product.product'].sudo()
        ItemLines = self.env['update.item.line.wizard'].sudo()
        States = self.env['res.country.state'].sudo()
        Country = self.env['res.country'].sudo()
        import_file = self.item_file
        try:
            wb = openpyxl.load_workbook(

                filename=BytesIO(base64.b64decode(import_file)), read_only=True
            )
            item_file_datas = []
            production_ids = []
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
                if not state_code:
                    state_id = False
                else:
                    state_id = States.search([('code', '=', state_code)], limit=1)
                country_code = record[8]
                if not country_code:
                    country_id = False
                else:
                    state_id = Country.search([('code', '=', country_code)], limit=1)
                zip = record[9]
                phone = record[10]
                email = record[11]

                if not sku or not production_id:
                    continue
                else:
                    if production_id and production_id not in production_ids:
                        production_id = production_id.strip()
                        production_ids.append(production_id)
                        item = Items.search([('production_id', '=', production_id)], limit=1)
                        product_id = Products.search([('default_code', '=', sku.strip())], limit=1)
                        if item and product_id:
                            item_file_datas.append({
                                'production_id': production_id,
                                'sale_order_line_id': item.id,
                                'product_id': product_id.id,
                                'personalize': personalize,
                            })

            item_ids = ItemLines.create(item_file_datas)
            self.line_ids = [(6, 0, item_ids.ids)]

        except:
            raise ValidationError(_('Insert Invalid File'))

    def action_update_item(self):
        line_ids = self.line_ids
        for line in line_ids:
            item = line.sale_order_line_id
            item.write({
                'product_id': line.product_id.id,
                'personalize': line.personalize
            })



class UpdateOrderLineWizard(models.TransientModel):
    _name = 'update.order.line.wizard'

    update_item_wizard_id = fields.Many2one('update.item.wizard')
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