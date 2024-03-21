# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pytz


class UpdateDesignerWizard(models.TransientModel):
    _name = 'update.designer.wizard'

    employee_id = fields.Many2one('hr.employee', required=True)
    item_ids = fields.Many2many('sale.order.line')

    def action_update_designer(self):
        items = self.item_ids
        employee_id = self.employee_id
        for item in items:
            item.write({
                'designer_id': employee_id.id
            })
