from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ItemProductionLine(models.Model):
    _name = 'item.production.line'
    _description = 'Production Line'
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
                raise ValidationError(_("This Production Line Code already exists."))