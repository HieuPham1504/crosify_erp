from odoo import api, fields, models

class FulfillShelfType(models.Model):
    _name = 'fulfill.shelf.type'
    _description = 'Shelf Type'

    shelf_type_name = fields.Char(string='Shelf Type Name')
    