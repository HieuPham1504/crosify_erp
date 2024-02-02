from odoo import api, fields, models

class FulfillShelfType(models.Model):
    _name = 'fulfill.shelf.type'
    _description = 'Shelf Type'

    shelf_type_name = fields.Char(string='Shelf Type Name')
    
    @api.depends('shelf_type_name')
    def _compute_display_name(self):

        for rec in self.sudo():
                rec.display_name = rec.shelf_type_name