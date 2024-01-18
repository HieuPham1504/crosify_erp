# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLineLevel(models.Model):
    _name = 'sale.order.line.level'
    _order = "level ASC"

    level = fields.Char(string='Level')
    name = fields.Char(string='Level Name')
    parent_id = fields.Many2one('sale.order.line.level', string='Parent Level')
    is_parent = fields.Boolean(string='Is Parent')
    next_level_ids = fields.Many2many('sale.order.line.level', 'sol_level_next_step_rel', 'level_id', 'next_level_id', string='Next Levels')
    active = fields.Boolean(string='Active', default=True)