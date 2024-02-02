from odoo import api, fields, models

class ShelfType(models.Model):
    _name = 'sale.order.shelf.type'
    _description = 'Shelf Type'

    shelf_type_name = fields.Char(string='Shelf Type Name')
    id = fields.Integer(string='ID', default=lambda self: self.env['ir.sequence'].next_by_code('sale.order.shelf.type'), readonly=True)
    