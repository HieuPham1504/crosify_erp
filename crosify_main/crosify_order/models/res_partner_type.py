# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class PartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Res partner type'

    name = fields.Char('Name', required=1)
    prefix_code = fields.Char('Prefix Code', required=1)
    code = fields.Char(string='Code', compute='_compute_code', store=True, readonly=False)
    padding = fields.Integer(string='Padding', required=1, default=3)
    sequence_id = fields.Many2one('ir.sequence')

    @api.model_create_multi
    def create(self, values):
        partner_type_ids = super().create(values)

        for partner_type_id in partner_type_ids:
            sequence_id = partner_type_id.create_ir_sequence()
            partner_type_id.sequence_id = sequence_id

        return partner_type_ids

    def unlink(self):
        customer_partner_id = self.env.ref('crosify_order.customer_partner_type').id
        for rec in self:
            if customer_partner_id == rec.id:
                raise UserError("Can't delete this record %s!" % rec.name)
            rec.sequence_id.unlink()
        return super(PartnerType, self).unlink()


    def create_ir_sequence(self):
        vals = {
            'name': "Res Partner Code" + str(self.name),
            'code': self.code,
            'prefix': self.prefix_code,
            'padding': self.padding,
            'implementation': 'standard',
            'number_increment': 1,
            'company_id': self.env.company.id,
        }
        sequence = self.env['ir.sequence'].create(vals)

        return sequence

    @api.depends('prefix_code')
    def _compute_code(self):
        for rec in self:
            if rec.prefix_code:
                rec.code = 'res.partner.' + rec.prefix_code
            else:
                rec.code = 'res.partner.' + str(rec.id)

    @api.depends('code')
    def _handle_code_sequence_id(self):
        for rec in self:
            if rec.sequence_id:
                rec.sequence_id.code = rec.prefix_code

