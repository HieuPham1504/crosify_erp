# -*- coding: utf-8 -*-
import openpyxl
import base64
from io import BytesIO
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class UpdateItemDesignWizard(models.TransientModel):
    _name = 'update.item.design.wizard'

    item_ids = fields.One2many('update.item.design.line.wizard', 'update_item_design_wizard_id', string='Items')
    item_design_file = fields.Binary(string='Design File')
    item_design_file_name = fields.Char(string='Design File Name')

    @api.model
    def action_update_item_design_info(self):
        Items = self.env['sale.order.line'].sudo()
        awaiting_items = Items.search([('sublevel_id.level', '=', 'L3.1')])

        item_datas = []
        for item in awaiting_items:
            item_datas.append((0, 0, {
                'sale_order_line_id': item.id
            }))

        return {
            "type": "ir.actions.act_window",
            "res_model": "update.item.design.wizard",
            "context": {
                "default_item_ids": item_datas,
            },
            "name": "Update Design File",
            'view_mode': 'form',
            "target": "current",
        }

    def action_update_design_file(self):
        current_employee = self.env.user.employee_id
        designed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L3.2')], limit=1)
        if not designed_level:
            raise ValidationError('There is no state with level Designed')
        for rec in self.sale_order_line_ids:
            design_file_url = rec.design_file_url
            rec.write({
                'design_file_url': design_file_url,
                'design_date': fields.Datetime.now(),
                'designer_id': current_employee.id,
                'sublevel_id': designed_level.id,
            })

    def get_import_templates(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'Get Import Template',
            'url': '/crosify_order/static/xls/import_design_file_template.xlsx',
        }

    def action_import_item_design_file(self):
        import_file = self.item_design_file

        total_lines = self.item_ids
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
                design_file_url = record[2]
                if not production_id or not design_file_url:
                    continue
                else:
                    production_id = production_id.strip()
                    if production_id and production_id not in production_ids:
                        production_ids.append(production_id)
                        item = total_lines.filtered(lambda item: item.production_id == production_id)

                        if item:
                            item.write({
                                'design_file_url': design_file_url,
                            })


        except:
            raise ValidationError(_('Insert Invalid File'))

    def action_update_design_file(self):
        designed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L3.2')], limit=1)
        if not designed_level:
            raise ValidationError('There is no state with level Designed')

        current_employee = self.env.user.employee_id
        items = self.item_ids
        updated_items = items.filtered(lambda item: item.design_file_url)
        for item in updated_items:
            sale_order_line_id = item.sale_order_line_id
            design_file_url = item.design_file_url
            sale_order_line_id.write({
                'design_file_url': design_file_url,
                'design_date': datetime.now(),
                'designer_id': current_employee.id,
                'sublevel_id': designed_level.id,
            })
        updated_items.unlink()

class UpdateItemDesignLineWizard(models.TransientModel):
    _name = 'update.item.design.line.wizard'
    _order = 'design_file_url ASC'

    update_item_design_wizard_id = fields.Many2one('update.item.design.wizard')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item')
    production_id = fields.Char(string='Production ID', related='sale_order_line_id.production_id')
    product_type = fields.Char(string='Product Type', related='sale_order_line_id.product_type')
    sublevel_id = fields.Many2one('sale.order.line.level', related='sale_order_line_id.sublevel_id')
    design_file_url = fields.Text(string='Design File Url')