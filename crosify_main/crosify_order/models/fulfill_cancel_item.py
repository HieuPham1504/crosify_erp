from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FulfillCancelItem(models.Model):
    _name = 'fulfill.cancel.item'
    _description = 'Cancel Item'

    name = fields.Char(string='Reason Cancel', required=True)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            name = record.name
            duplicate_name = self.sudo().search(
                [('id', '!=', record.id), ('name', '=', name)])
            if duplicate_name:
                raise ValidationError(_("This Cancel Item already exists."))
    