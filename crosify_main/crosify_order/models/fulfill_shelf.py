from odoo import api, fields, models

class FulfillShelf(models.Model):
    _name = 'fulfill.shelf'
    _description = 'Shelf'

    shelf_code = fields.Char(string='Shelf Code')
    shelf_name = fields.Char(string='Shelf Name')
    shelf_type = fields.Many2one('fulfill.shelf.type', string='Shelf Type')

        

    
    