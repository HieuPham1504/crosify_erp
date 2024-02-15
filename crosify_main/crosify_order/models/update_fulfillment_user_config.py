from odoo import api, fields, models

class UpdateFulfillmentUserConfig(models.Model):
    _name = 'update.fulfillment.user.config'
    _description = 'Update Fulfillment User Config'
    _order = "sequence"
    _rec_name = "user_field_description"

    is_active = fields.Boolean(string='Active', default=True)
    user_field_name = fields.Char(string='Field Name', required=True)
    user_field_description = fields.Char(string='Field Description', required=True)
    sequence = fields.Integer(string='Sequence', required=True)