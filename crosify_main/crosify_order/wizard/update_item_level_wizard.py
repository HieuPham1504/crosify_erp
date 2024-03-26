
# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pytz


class UpdateItemLevelWizard(models.TransientModel):
    _name = 'update.item.level.wizard'

    level_id = fields.Many2one('sale.order.line.level', required=True)
    item_ids = fields.Many2many('sale.order.line')
    def action_update_item_level(self):
        items = self.item_ids
        level_id = self.level_id
        for item in items:
            item.write({
                'sublevel_id': level_id.id,
                'level_id': level_id.parent_id.id
            })

