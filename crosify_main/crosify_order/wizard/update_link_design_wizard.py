# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import openpyxl
import base64
from io import BytesIO


class UpdateLinkDesignWizard(models.TransientModel):
    _name = 'update.link.design.wizard'

    item_design_file = fields.Binary(string='Design File')
    item_design_file_name = fields.Char(string='Design File Name')

    def get_import_templates(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'Get Import Template',
            'url': '/crosify_order/static/xls/import_update_link_design_file_template.xlsx',
        }

    def action_import_item_design_file(self):
        import_file = self.item_design_file

        total_lines = self.env['sale.order.line'].search([('sublevel_id.level', '=', 'L3.1')])
        designed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L3.2')], limit=1)
        current_employee = self.env.user.employee_id
        if not designed_level:
            raise ValidationError('There is no state with level Designed')
        try:
            wb = openpyxl.load_workbook(

                filename=BytesIO(base64.b64decode(import_file)), read_only=True
            )
            production_ids = []
            ws = wb.active
            for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,
                                       max_col=None, values_only=True):
                production_id = record[0]
                design_file_url = record[1]
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
                                'sublevel_id': designed_level.id,
                                'design_date': datetime.now(),
                                'designer_id': current_employee.id,
                            })
        except Exception:
            raise ValidationError(_('Insert Invalid File'))


