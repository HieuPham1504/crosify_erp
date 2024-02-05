from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTypeShelfType(models.Model):
    _name = 'product.type.shelf.type'
    _description = 'Product Type - Shelf Type'

    product_type_id = fields.Many2one('product.template', string='Product Type', required=True)
    shelf_type_id = fields.Many2one('fulfill.shelf.type', string='Shelf Type', required=True)
    print(product_type_id)
    @api.constrains('product_type_id')
    def _check_product_type(self):
        for rec in self.sudo():
                product_type_id = rec.product_type_id.id
                duplicate_type = self.sudo().search(
                    [('id', '!=', rec.id), ('product_type_id', '=', product_type_id)])
                if duplicate_type:
                    raise ValidationError(_("This product type has been used for another shelf type.")) 