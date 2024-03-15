import io
import json
import xlsxwriter
from odoo.tools import date_utils


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MOProduction(models.Model):
    _name = 'mo.production'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production'
    _rec_name = 'code'
    _order = 'date desc'

    code = fields.Char(string='Code')
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
                                  default=lambda self: self.env.user.employee_id.id)
    note = fields.Text(string='Note')
    mo_production_line_ids = fields.Many2many('sale.order.line', 'mo_production_so_line_rel', string='Items')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('production', 'Production')
    ], string='State', default='draft', index=True, tracking=1)

    @api.constrains('mo_production_line_ids')
    def constraint_sale_order_line_id(self):
        for rec in self:
            for item in rec.mo_production_line_ids:
                duplicate_item = self.sudo().search(
                    [('mo_production_line_ids', 'in', item.ids), ('id', '!=', rec.id)])
                if duplicate_item:
                    raise ValidationError(
                        _(f"This Item {item.display_name} already exists in Productions {','.join(code for code in duplicate_item.mapped('code'))}"))

    def action_export_xlsx(self):
        data = {
            'id': self.id,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': f'{self._name}',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Production Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        production_id = data.get('id')
        production = self.sudo().browse(production_id)

        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'align': 'center'})

        headers = [
            'Production Line',
            'Fulfill Note',
            'Order ID Fix',
            'Production ID',
            'Quantity',
            'Product Type',
            'SKU',
            'Per',
            'Design Link',
            'Domain',
        ]

        header_row = 0
        col = 0
        for header in headers:
            worksheet.write(header_row, col, header, style_highlight)
            worksheet.set_column(col, col, 15)
            col += 1


        line_row = 1
        mo_production_line_ids = production.mo_production_line_ids
        for line in mo_production_line_ids:
            production_line = line.production_line_id.name if line.production_line_id else ''
            fulfill_note = line.note_fulfill if line.note_fulfill else ''
            order_id_fix = line.order_id_fix if line.order_id_fix else ''
            production_id = line.production_id if line.production_id else ''
            product_type = line.product_type if line.product_type else ''
            sku = line.product_id.default_code if line.product_id.default_code else ''
            personalize = line.personalize if line.personalize else ''
            design_file_url = line.design_file_url if line.design_file_url else ''
            domain = line.order_id.domain if line.order_id.domain else ''

            worksheet.write(line_row, 0, production_line, cell_format)
            worksheet.write(line_row, 1, fulfill_note, cell_format)
            worksheet.write(line_row, 2, order_id_fix, cell_format)
            worksheet.write(line_row, 3, production_id, cell_format)
            worksheet.write(line_row, 4, 1, cell_format)
            worksheet.write(line_row, 5, product_type, cell_format)
            worksheet.write(line_row, 6, sku, cell_format)
            worksheet.write(line_row, 7, personalize, cell_format)
            worksheet.write(line_row, 8, design_file_url, cell_format)
            worksheet.write(line_row, 9, domain, cell_format)
            line_row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    @api.model_create_multi
    def create(self, vals_list):
        results = super(MOProduction, self).create(vals_list)
        for val in results:
            if not val.code:
                val.code = self.env['ir.sequence'].sudo().next_by_code('mo.production.code') or _('New')
        return results

    def action_set_item_start_info(self):
        for line in self.mo_production_line_ids:
            data = {}
            if self.date:
                data.update({
                    'production_start_date': self.date
                })
            if self.note:
                data.update({
                    'production_note': self.note
                })
            line.write(data)

    def action_produce_items(self):
        production_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.1')], limit=1)
        if not production_level:
            raise ValidationError('There is no state with level Production')
        for rec in self:
            if not rec.mo_production_line_ids:
                continue
            for item in rec.mo_production_line_ids:
                item.write({
                    'sublevel_id': production_level.id,
                    'level_id': production_level.parent_id.id,
                })
            rec.action_set_item_start_info()
            rec.state = 'production'

    def action_back_to_fulfill_vendor_items(self):
        fulfill_vendor_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.0')], limit=1)
        if not fulfill_vendor_level:
            raise ValidationError('There is no state with level Fulfill Vendor')
        for rec in self:
            for item in rec.mo_production_line_ids:
                item.write({
                    'sublevel_id': fulfill_vendor_level.id,
                    'level_id': fulfill_vendor_level.parent_id.id,
                    'production_start_date': False
                })
            rec.state = 'draft'
