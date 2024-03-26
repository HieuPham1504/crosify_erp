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

    def unlink(self):
        current_user = self.env.user
        operator_user = current_user.has_group('crosify_order.group_sale_team_operator')
        system_user = current_user.has_group('base.group_system')
        if operator_user or system_user:
            if any([rec.state != 'draft' for rec in self]):
                raise ValidationError(_('Can Not Delete Record'))
        else:
            raise ValidationError(_('Can Not Delete Record'))
        res = super().unlink()
        return res

    def transfer_items(self):
        for rec in self:
            if not rec.production_transfer_item_ids:
                raise ValidationError(_('Can Not Transfer None Transferred Item'))
            rec.state = 'waiting_confirm'

    def back_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def qc_confirm(self):
        package_receive_level = self.env['sale.order.line.level'].sudo().search([('level', '=', 'L4.2')], limit=1)
        if not package_receive_level:
            raise ValidationError('There is no Package Receive Level')
        for rec in self:
            if not rec.qc_receive_item_ids:
                raise ValidationError(_('Can Not Confirm None Received Item'))
            production_transfer_item_ids = rec.production_transfer_item_ids
            qc_receive_item_ids_obj = rec.qc_receive_item_ids

            for transfer_item in qc_receive_item_ids_obj.mapped('sale_order_line_id'):
                transfer_item.write({
                    'sublevel_id': package_receive_level.id,
                    'production_done_date': fields.Date.today(),
                })

            transfer_item_ids = production_transfer_item_ids.mapped('sale_order_line_id').ids
            qc_receive_item_ids = qc_receive_item_ids_obj.mapped('sale_order_line_id').ids

            lack_item_ids = set(transfer_item_ids) - set(qc_receive_item_ids)
            redundant_item_ids = set(qc_receive_item_ids) - set(transfer_item_ids)

            errors = []
            if len(lack_item_ids) > 0:
                for lack_item in lack_item_ids:
                    errors.append((0, 0, {
                        'sale_order_line_id': lack_item,
                        'status': 'lack'
                    }))
            if len(redundant_item_ids) > 0:
                for redundant_item in redundant_item_ids:
                    errors.append((0, 0, {
                        'sale_order_line_id': redundant_item,
                        'status': 'redundant'
                    }))

            rec.production_transfer_item_error_ids = errors
            # production_transfer_item_ids.filtered(lambda item: item.sale_order_line_id.id in list(lack_item_ids)).sudo().unlink()
            # qc_receive_item_ids_obj.filtered(lambda item: item.sale_order_line_id.id in list(redundant_item_ids)).sudo().unlink()


            rec.state = 'confirm'






