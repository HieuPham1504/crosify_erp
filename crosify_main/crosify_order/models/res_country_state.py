# -*- coding: utf-8 -*-
import json
import requests
import random
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    service_type = fields.Integer(string='Service Type', index=True)