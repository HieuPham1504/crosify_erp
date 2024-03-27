# -*- coding: utf-8 -*-
import contextlib
import collections
import requests
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.models import BaseModel

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'SKU'

    @api.constrains('default_code')
    def _check_default_code(self):
        for record in self:
            default_code = record.default_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('default_code', '=', default_code)])
            if duplicate_code:
                raise ValidationError(_("This SKU already exists."))

    default_code = fields.Char(string='SKU')
    product_tmpl_product_type = fields.Char(string='SKU Type', related='product_tmpl_id.product_type', store=True,
                                            index=True)
    weight = fields.Float(string='Weight (Gram)')
    length = fields.Float(string='Length (cm)')
    width = fields.Float(string='Width (cm)')
    height = fields.Float(string='Height (cm)')
    vendor_production_price_ids = fields.One2many('product.vendor.production.price', 'product_id',
                                                  string='Production Price')
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id.id, tracking=True)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res_ids = super(ProductProduct, self).create(vals_list)
    #     for res_id in res_ids:
    #         res_id.with_delay(
    #                 description=f'Sync product_id = {res_id.default_code}',
    #                 channel='root.product').sync_sku_myadmin()
    #     return res_ids
    #
    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         if vals.get('product_template_attribute_value_ids'):
    #             rec.with_delay(
    #                 description=f'Sync product_id = {rec.default_code}',
    #                 channel='root.product').sync_sku_myadmin()
    #
    #     return res


    @api.depends("product_tmpl_id.write_date")
    def _compute_write_date(self):
        """
        First, the purpose of this computation is to update a product's
        write_date whenever its template's write_date is updated.  Indeed,
        when a template's image is modified, updating its products'
        write_date will invalidate the browser's cache for the products'
        image, which may be the same as the template's.  This guarantees UI
        consistency.

        Second, the field 'write_date' is automatically updated by the
        framework when the product is modified.  The recomputation of the
        field supplements that behavior to keep the product's write_date
        up-to-date with its template's write_date.

        Third, the framework normally prevents us from updating write_date
        because it is a "magic" field.  However, the assignment inside the
        compute method is not subject to this restriction.  It therefore
        works as intended :-)
        """
        for record in self:
            record.write_date = max(record.write_date or self.env.cr.now(),
                                    record.product_tmpl_id.write_date) if record.product_tmpl_id.write_date else False

    def action_select_product_template(self):
        return {
            'name': 'Select Product',
            'view_mode': 'form',
            'res_model': 'select.product.template.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_id': self.id}
        }

    def sync_sku_myadmin(self):
        client_key = self.env['ir.config_parameter'].sudo().get_param('create.label.client.key')
        if not client_key:
            raise ValueError("Not Found Client Key")

        headers = {"Content-Type": "application/json",
                   "Accept": "application/json",
                   "Catch-Control": "no-cache",
                   "clientkey": f"{client_key}"}

        sku_code = self.default_code

        url = f"https://myadmin.crosify.com/api/sku/{sku_code}"

        color = ''
        size = ''
        other_option = ''

        attribute_ids = self.product_template_attribute_value_ids

        for attribute in attribute_ids:
            if attribute.attribute_line_id.attribute_id.code == 'color':
                color = attribute.name
            if attribute.attribute_line_id.attribute_id.code == 'size':
                size = attribute.name
            if attribute.attribute_line_id.attribute_id.code == 'other_option':
                other_option = attribute.name

        json_data = {
            "COLOR": color,
            "SIZE": size,
            "OTHEROPTION": other_option
        }

        return requests.put(url, data=json.dumps(json_data), headers=headers)