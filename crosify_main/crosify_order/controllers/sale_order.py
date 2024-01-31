# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import http
import requests
from odoo.http import Controller, request, Response, route

import hmac
import hashlib
import base64

class SaleOrderController(Controller):

    def verify_webhook(self, data, hmac_header):
        CLIENT_SECRET = request.env['ir.config_parameter'].sudo().get_param('hmac_sha256_secret', False)
        digest = hmac.new(CLIENT_SECRET.encode('utf-8'), data, digestmod=hashlib.sha256).digest()
        computed_hmac = base64.b64encode(digest)

        return hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))
    @route("/api/sale_orders", methods=["POST"], type="json", auth="public", cors="*")
    def action_create_sale_order(self, **kwargs):
        data = request.get_json_data()
        verified = self.verify_webhook(data, request.httprequest.headers['X-Crosify-Hmac-SHA256'])
        if not verified:
            return Response("Bad Request", status=400)
        else:
            Response.status = "400 Bad Request"
            return Response("Success", status=200)