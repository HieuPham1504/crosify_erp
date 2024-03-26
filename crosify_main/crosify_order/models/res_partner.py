import re
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    res_partner_code = fields.Char(string='Code')
    partner_type_id = fields.Many2one(comodel_name='res.partner.type',
                                      copy=False,
                                      string='Contact Type',
                                      default=lambda self: self.env.ref('crosify_order.customer_partner_type'))

    @api.model
    def create(self, vals):
        if not vals.get('res_partner_code'):
            if vals.get('partner_type_id'):
                code = self.get_code_ir_sequence(vals.get('partner_type_id'))
            else:
                code = False

            if code:
                vals['res_partner_code'] = self.env['ir.sequence'].next_by_code(code)

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
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = args[:]
        if name:
            domain = ['|', ('name', operator, name), ('res_partner_code', operator, name)]
            domain += args
        partners = self.search(domain, limit=limit)
        return partners.name_get()
    
    @api.model
    def action_generate_code_for_partner_model(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        items.action_generate_code_for_partner()
    def action_generate_code_for_partner(self):
        for rec in self:
            if not rec.res_partner_code:
                if rec.partner_type_id:
                    code = self.get_code_ir_sequence(rec.partner_type_id.id)
                else:
                    code = False

                if code:
                    rec.res_partner_code = self.env['ir.sequence'].next_by_code(code)
                else:
                    rec.res_partner_code = self.env['ir.sequence'].next_by_code('res.partner.code')

    def get_code_ir_sequence(self, partner_type_id):
        partner_type_obj = self.env['res.partner.type'].sudo().browse(int(partner_type_id)).exists()
        code = False
        if partner_type_obj:
            code = partner_type_obj.code
        return code
