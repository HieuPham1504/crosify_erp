from odoo import api, fields, models

class ShelfType(models.Model):
    _name = 'fulfill.shelf.type'
    _description = 'Shelf Type'

    shelf_type_name = fields.Char(string='Shelf Type Name')
    # id = fields.Integer(string='ID', readonly=True)
    