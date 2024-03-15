from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class OrderShippingLine(models.Model):
    _name = 'order.shipping.line'
    _description = 'Shipping Line'
    _rec_name = 'name'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            code = record.code
            duplicate_type = self.sudo().search(
                [('id', '!=', record.id), ('code', '=', code)])
            if duplicate_type:
                raise ValidationError(_("This Shipping Line Code already exists."))