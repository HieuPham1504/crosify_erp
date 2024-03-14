# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pytz


class OrderBoxContainer(models.Model):
    _name = 'order.box.container'
    _order = 'code ASC'

    code = fields.Char(string='Code', required=True, index=True)
    name = fields.Char(string='Name', required=True)