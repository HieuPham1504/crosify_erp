# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RaiseInformationWizard(models.TransientModel):
    _name = 'raise.information.wizard'

    warning = fields.Text(string='Warning')