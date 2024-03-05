from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HSProductConfig(models.Model):
    _name = 'hs.product.config'
    _description = 'HS Product Config'
    _rec_name = 'hs_code'

    @api.constrains('hs_code')
    def _check_hs_code(self):
        for record in self:
            hs_code = record.hs_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('hs_code', '=', hs_code)])
            if duplicate_code:
                raise ValidationError(_("This HS Code has been used for another Config."))

    hs_code = fields.Char(string='HS Code', required=True, index=1)
    product_ename = fields.Char(string='Product EName', required=True)
    product_cname = fields.Char(string='Product CName', required=True)

