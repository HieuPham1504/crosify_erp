# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    request_code = fields.Char(string='Request Code')

    @api.model_create_multi
    def create(self, vals_list):
        today_format = fields.Date.today().strftime('%d/%d/%Y').replace('/', '')
        requests = super(ApprovalRequest, self).create(vals_list)
        for request in requests:
            if not request.request_code:
                category_name = request.category_id.name if request.category_id else ''
                seq_surfix = self.env['ir.sequence'].next_by_code('stock.lot.serial') or '/'
                request_code = f'{category_name}{today_format}{seq_surfix}'
                request.request_code = request_code
        return requests