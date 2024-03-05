# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CheckingPackedItemWizard(models.TransientModel):
    _name = 'checking.packed.item.wizard'
    _rec_name = 'name'