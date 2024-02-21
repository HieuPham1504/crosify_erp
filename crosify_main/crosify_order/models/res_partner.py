from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    res_partner_code = fields.Char(string='Code')

    @api.model
    def create(self, vals):
        if not vals.get('res_partner_code'):
            vals['res_partner_code'] = self.env['ir.sequence'].next_by_code('res.partner.code') or '/'
        return super(ResPartner, self).create(vals)
    
    @api.depends('name', 'res_partner_code')
    @api.depends_context('res_partner_code', 'name')
    def _compute_display_name(self):
        def get_display_name(name, code):
            if self._context.get('display_partner_name', True) and code:
                return f'[{code}] - {name}'
            return name
        for rec in self.sudo():
                rec.display_name = get_display_name(rec.name, rec.res_partner_code)