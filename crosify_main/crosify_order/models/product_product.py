# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'SKU'

    @api.constrains('default_code')
    def _check_description(self):
        for record in self:
            default_code = record.default_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('default_code', '=', default_code)])
            if duplicate_code:
                raise ValidationError(_("This SKU already exists."))

    default_code = fields.Char(string='SKU')
    product_tmpl_product_type = fields.Char(string='Product Type', related='product_tmpl_id.product_type', store=True,
                                            index=True)
    weight = fields.Float(string='Weight (Gram)')
    length = fields.Float(string='Length (cm)')
    width = fields.Float(string='Width (cm)')
    height = fields.Float(string='Height (cm)')
    vendor_production_price_ids = fields.One2many('product.vendor.production.price', 'product_id',
                                                  string='Production Price')

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
