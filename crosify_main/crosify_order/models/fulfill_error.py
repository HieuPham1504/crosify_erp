from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FulfillError(models.Model):
    _name = 'fulfill.error'
    _description = 'Error Type'

    error_type = fields.Char(string='Error Type', required=True)

    @api.constrains('error_type')
    def _check_error_type(self):
        for record in self:
            error_type = record.error_type
            duplicate_type = self.sudo().search(
                [('id', '!=', record.id), ('error_type', '=', error_type)])
            if duplicate_type:
                raise ValidationError(_("This Error Type already exists."))