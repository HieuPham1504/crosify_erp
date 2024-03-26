
# -*- coding: utf-8 -*-
import pytz
import openpyxl
import base64
from io import BytesIO
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UpdateItemWizard(models.TransientModel):
    _name = 'update.item.wizard'
    _rec_name = 'name'

    name = fields.Char(default='Update Item')
    item_file = fields.Binary(string='Items File')
    item_file_name = fields.Char(string='Items')
    line_ids = fields.One2many('update.item.line.wizard', 'update_item_wizard_id', string='Update Items')

    def action_import_items(self):
        Items = self.env['sale.order.line'].sudo()
        Products = self.env['product.product'].sudo()
        ItemLines = self.env['update.item.line.wizard'].sudo()
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
                production_id = record[1]
                sku = record[2]
                personalize = record[3]
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

    def get_import_templates(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'Get Import Template',
            'url': '/crosify_order/static/xls/import_item_template.xlsx',
        }

    def action_update_item(self):
        line_ids = self.line_ids
        for line in line_ids:
            item = line.sale_order_line_id
            item.write({
                'product_id': line.product_id.id,
                'personalize': line.personalize
            })



class UpdateItemLineWizard(models.TransientModel):
    _name = 'update.item.line.wizard'

    update_item_wizard_id = fields.Many2one('update.item.wizard')
    production_id = fields.Char(string='Production ID', required=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item')
    product_id = fields.Many2one('product.product', string='SKU')
    personalize = fields.Char(string='Personalize')
