from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MOProductionLine(models.Model):
    _name = 'mo.production.line'
    _description = 'Production Lines'

    _sql_constraints = [('item_uniq', "unique(production_id, sale_order_line_id)",
                         "This Item already exists.")]

    production_id = fields.Many2one('mo.production', string='Production', required=True, ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Item', required=True, domain="[('sublevel_id.level', '=', 'L3.2')]")
    product_id = fields.Many2one('product.product', string='SKU', related='sale_order_line_id.product_id', store=True, index=True)
    attribute_value_ids = fields.Many2many('product.template.attribute.value', compute='compute_attribute_value_ids', store=True)

    @api.constrains('sale_order_line_id')
    def constraint_sale_order_line_id(self):
        for rec in self:
            item = rec.sale_order_line_id
            production_id = rec.production_id
            duplicate_item = self.sudo().search([('sale_order_line_id', '=', item.id), ('production_id', '!=', production_id.id)])
            if duplicate_item:
                raise ValidationError(_(f"This Item already exists in Productions {','.join(code for code in duplicate_item.production_id.mapped('code'))}"))

    @api.depends('product_id.product_template_attribute_value_ids')
    def compute_attribute_value_ids(self):
        for rec in self:
            attribute_value_ids = rec.product_id.product_template_attribute_value_ids.ids if rec.product_id else []
            rec.attribute_value_ids = [(6, 0, attribute_value_ids)]