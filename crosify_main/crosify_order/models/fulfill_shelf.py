from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FulfillShelf(models.Model):
    _name = 'fulfill.shelf'
    _description = 'Shelf'
    _rec_name = 'shelf_name'

    shelf_code = fields.Char(string='Shelf Code')
    shelf_name = fields.Char(string='Shelf Name')
    shelf_type = fields.Many2one('fulfill.shelf.type', string='Shelf Type')
    max_shelf = fields.Integer(string='Max Shelf', default=1)
    current_shelf = fields.Integer(string='Current Shelf')

    @api.constrains('shelf_code')
    def _check_shelf_code(self):
        for record in self:
            shelf_code = record.shelf_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('shelf_code', '=', shelf_code)])
            if duplicate_code:
                raise ValidationError(_("This shelf code has been used for another shelf."))

    
    