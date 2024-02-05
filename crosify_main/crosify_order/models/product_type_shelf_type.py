from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTypeShelfType(models.Model):
    _name = 'product.type.shelf.type'
    _description = 'Product Type - Shelf Type'

    product_tmp_id = fields.Many2one('product.template', string='Product Type', required=True)
    shelf_type_id = fields.Many2one('fulfill.shelf.type', string='Shelf Type', required=True)

    @api.constrains('product_tmp_id')
    def _check_product_type(self):
        for rec in self.sudo():
                product_tmp_id = rec.product_tmp_id.id
                duplicate_type = self.sudo().search(
                    [('id', '!=', rec.id), ('product_tmp_id', '=', product_tmp_id)])
                if duplicate_type:
                    raise ValidationError(_("This product type has been used for another shelf type.")) 