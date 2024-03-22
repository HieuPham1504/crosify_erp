from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrosifySeller(models.Model):
    _name = 'crosify.seller'
    _description = 'Seller'
    _rec_name = 'code'

    @api.constrains('code')
    def _check_code(self):
        for record in self:
            code = record.code
            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('code', '=', code)])
            if duplicate_code:
                raise ValidationError(_("This Seller Code already exists."))

    code = fields.Char(string='Code', index=True, required=False)
    name = fields.Char(string='Name', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        results = super(CrosifySeller, self).create(vals_list)
        for val in results:
            if not val.code:
                val.code = self.env['ir.sequence'].sudo().next_by_code('seller.code')
        return results
