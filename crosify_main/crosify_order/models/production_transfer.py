from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductionTransfer(models.Model):
    _name = 'production.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Production Transfer'
    _rec_name = 'code'

    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, index=True, default=lambda self: self.env.user.employee_id.id)
    note = fields.Text(string='Note')
    production_transfer_item_ids = fields.One2many('production.transfer.item', 'production_transfer_id', string='Production Transfer')
    qc_receive_item_ids = fields.One2many('qc.receive.item', 'production_transfer_id', string='QC Receive')
    production_transfer_item_error_ids = fields.One2many('production.transfer.item.error', 'production_transfer_id', string='Production Transfer Error')
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

    def transfer_items(self):
        for rec in self:
            rec.state = 'waiting_confirm'

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def qc_confirm(self):
        QCReceives = self.env['qc.receive.item'].sudo()
        TransferItems = self.env['production.transfer.item'].sudo()
        TransferItemErrors = self.env['production.transfer.item.error'].sudo()
        package_receive_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.2')], limit=1)
        if not package_receive_level:
            raise ValidationError('There is no Package Receive Level')
        for rec in self:
            production_transfer_item_ids = rec.production_transfer_item_ids
            qc_receive_item_ids = rec.qc_receive_item_ids
            transfer_production_ids = production_transfer_item_ids.mapped('production_id')
            qc_receive_production_ids = qc_receive_item_ids.mapped('production_id')
            transfer_diff_production_ids = set(transfer_production_ids) - set(qc_receive_production_ids)
            redundant_production_ids = set(qc_receive_production_ids) - set(transfer_production_ids)
            if len(transfer_diff_production_ids) == 0:
                qc_diff_production_ids = set(qc_receive_production_ids) - set(transfer_production_ids)
                if len(qc_diff_production_ids) > 0:
                    production_ids = list(qc_diff_production_ids)
                    qc_receive_ids = qc_receive_item_ids.filtered(lambda qc: qc.production_id in production_ids)

                    qc_receive_ids.unlink()
                for transfer_item in production_transfer_item_ids.mapped('sale_order_line_id'):
                    transfer_item.sublevel_id = package_receive_level.id
                    transfer_item.write({
                        'sublevel_id': package_receive_level.id,
                        'production_done_date': fields.Date.today(),
                    })
                rec.state = 'confirm'
            else:
                diff_transfer_productions = list(transfer_diff_production_ids)
                transfer_item_ids = production_transfer_item_ids.filtered(lambda transfer: transfer.production_id in diff_transfer_productions)
                not_available_productions = []
                for transfer_item in transfer_item_ids:
                    transfer_item.is_wrong_item = True
                    not_available_productions.append(transfer_item.production_id)

                not_available_productions_str = ','.join([production for production in not_available_productions])
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'raise.information.wizard',
                    'views': [[self.env.ref('crosify_order.raise_information_wizard_form_view').id, 'form']],
                    'context': {
                        'default_warning': f'Not Available Transfer Item With Production ID: {not_available_productions_str}'
                    },
                    'target': 'new',
                }





