# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'

    code = fields.Char(string='Code')

    _sql_constraints = [
        ('code_unique', 'unique (code)', "The code must be unique."),
    ]