# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    request_code = fields.Char(string='Request Code')

    @api.model_create_multi
    def create(self, vals_list):
        today_format = fields.Date.today().strftime('%d/%d/%Y').split('/')
        date = today_format[0]
        month = today_format[1]
        year = today_format[-1][-2:]
        requests = super(ApprovalRequest, self).create(vals_list)
        for request in requests:
            if not request.request_code:
                category_name = request.category_id.name if request.category_id else ''
                seq_surfix = self.env['ir.sequence'].next_by_code('approval.request') or '/'
                request_code = f'{category_name}{date}{month}{year}{seq_surfix}'
                request.request_code = request_code
        return requests