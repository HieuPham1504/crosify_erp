from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FulfillError(models.Model):
    _name = 'fulfill.error'
    _description = 'Error Type'
    _rec_name = 'error_type'

    error_type = fields.Char(string='Error Type', required=True)
    level_back_id = fields.Many2one('sale.order.line.level',
                                    string='Level Back',
                                    help="Level back when create new item QC Failed")

    @api.constrains('error_type')
    def _check_error_type(self):
        for record in self:
            error_type = record.error_type
            duplicate_type = self.sudo().search(
                [('id', '!=', record.id), ('error_type', '=', error_type)])
            if duplicate_type:
                raise ValidationError(_("This Error Type already exists."))