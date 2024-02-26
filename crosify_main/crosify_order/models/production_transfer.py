from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductionTransfer(models.Model):
    _name = 'production.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production Transfer'
    _rec_name = 'code'

    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, index=True)
    note = fields.Text(string='Note')
    production_transfer_item_ids = fields.One2many('production.transfer.item', 'production_transfer_id', string='Production Transfer')
    qc_receive_item_ids = fields.One2many('qc.receive.item', 'production_transfer_id', string='QC Receive')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_confirm', 'Wait Confirm'),
        ('confirm', 'Confirm')], string='State', default='draft', index=True, tracking=1)

    @api.model_create_multi
    def create(self, vals_list):
        results = super(ProductionTransfer, self).create(vals_list)
        for val in results:
            if not val.code:
                val.code = self.env['ir.sequence'].sudo().next_by_code('production.transfer') or _('New')
        return results


