# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    request_code = fields.Char(string='Request Code')

    @api.model_create_multi
    def create(self, vals_list):
        user_tz = pytz.timezone(self.env.context['tz'])
        time = fields.Date.to_string(user_tz.localize(fields.Datetime.from_string(datetime.now().date()),
                                                           is_dst=None).astimezone(pytz.utc))

        today_format_split = time.split('-')
        date = today_format_split[-1]
        month = today_format_split[1]
        year = today_format_split[0][-2:]
        requests = super(ApprovalRequest, self).create(vals_list)
        for request in requests:
            if not request.request_code:
                category_name = request.category_id.name if request.category_id else ''
                seq_surfix = self.env['ir.sequence'].next_by_code('approval.request') or '/'
                request_code = f'{category_name}{date}{month}{year}{seq_surfix}'
                request.request_code = request_code
        return requests