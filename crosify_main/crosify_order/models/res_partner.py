import re
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
    @api.depends_context('show_address', 'partner_show_db_id', 'address_inline', 'show_email', 'show_vat')
    def _compute_display_name(self):
        for partner in self:
            name = partner.complete_name
            if partner.res_partner_code:
                name = f"[{partner.res_partner_code}] - {name}"
            if partner._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = re.sub(r'\s+\n', '\n', name)
            if partner._context.get('partner_show_db_id'):
                name = f"{name} ({partner.id})"
            if partner._context.get('address_inline'):
                splitted_names = name.split("\n")
                name = ", ".join([n for n in splitted_names if n.strip()])
            if partner._context.get('show_email') and partner.email:
                name = f"{name} <{partner.email}>"
            if partner._context.get('show_vat') and partner.vat:
                name = f"{name} ‒ {partner.vat}"

            partner.display_name = name.strip()