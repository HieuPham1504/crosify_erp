# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pytz


class UpdateDesignNoteWizard(models.TransientModel):
    _name = 'update.design.note.wizard'

    note = fields.Text(string='Note', required=True)
    item_ids = fields.Many2many('sale.order.line')

    def action_update_design_note(self):
        items = self.item_ids
        note = self.note
        full_filled_level_id = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L2.2')], limit=1)
        if not full_filled_level_id:
            raise UserError(_("No full filled level found. Please contact Admin."))
        for item in items:
            item.write({
                'design_note': note,
                'sublevel_id': full_filled_level_id.id
            })
