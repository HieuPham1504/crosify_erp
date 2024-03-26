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
    fields_ignore_ids = fields.Many2many(comodel_name='fields.ignore',
                                         relation='fulfill_error_field_ignore',
                                         column1='fulfill_error_id',
                                         column2='field_ignore_id',
                                         string='Fields Ignore'
                                         )

    @api.constrains('error_type')
    def _check_error_type(self):
        for record in self:
            error_type = record.error_type
            duplicate_type = self.sudo().search(
                [('id', '!=', record.id), ('error_type', '=', error_type)])
            if duplicate_type:
                raise ValidationError(_("This Error Type already exists."))


class FieldsIgnore(models.Model):
    _name = 'fields.ignore'
    _description = 'Fields Ignore'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one(comodel_name='ir.model', string='Applies to', ondelete='cascade',
                               default=lambda self: self.env.ref('sale.model_sale_order_line'),
                               help="Model on which the Server action for sending WhatsApp will be created.",
                               required=True, tracking=True)
    model = fields.Char(
        string='Related Document Model', related='model_id.model',
        index=True, precompute=True, store=True, readonly=True)