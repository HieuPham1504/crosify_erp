# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pytz


class CancelItemWizard(models.TransientModel):
    _name = 'cancel.item.wizard'

    cancel_reason_id = fields.Many2one('fulfill.cancel.item', string='Cancel Reason')
    cancel_note = fields.Text(string='Note')
    item_ids = fields.Many2many('sale.order.line')

    def action_cancel_items(self):
        cancel_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L7.2')], limit=1)
        now = datetime.now()
        if not cancel_level:
            raise ValidationError('There is no state with level Cancel')
        for item in self.item_ids:
            item.write({
                'cancel_reason_id': self.cancel_reason_id.id,
                'cancel_note': self.cancel_note,
                'cancel_date': now,
                'sublevel_id': cancel_level.id,
                'level_id': cancel_level.parent_id.id
            })


