# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class UpdateItemDesignWizard(models.TransientModel):
    _name = 'update.item.design.wizard'

    sale_order_line_ids = fields.Many2many('sale.order.line', 'update_design_sale_order_line_rel', string='Items', domain="[('sublevel_id.level', '=', 'L3.1')]")

    def action_update_design_file(self):
        current_employee = self.env.user.employee_id
        designed_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L3.2')], limit=1)
        if not designed_level:
            raise ValidationError('There is no state with level Designed')
        for rec in self.sale_order_line_ids:
            design_file_url = rec.design_file_url
            rec.write({
                'design_file_url': design_file_url,
                'design_date': fields.Datetime.now(),
                'designer_id': current_employee.id,
                'sublevel_id': designed_level.id,
            })