from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrderType(models.Model):
    _name = 'sale.order.type'
    _description = 'Order Type'
    _rec_name = 'order_type_name'

    order_type_name = fields.Char(string='Order Type', required=True)

    @api.constrains('order_type_name')
    def _check_order_type_name(self):
        for record in self:
            order_type_name = record.order_type_name
            duplicate_type = self.sudo().search(
                [('id', '!=', record.id), ('order_type_name', '=', order_type_name)])
            if duplicate_type:
                raise ValidationError(_("This Order Type already exists."))