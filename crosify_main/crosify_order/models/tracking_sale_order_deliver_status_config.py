from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class TrackingSaleOrderDeliverStatusConfig(models.Model):
    _name = 'tracking.sale.order.deliver.status.config'
    _description = 'Tracking Sale Order Deliver Status Config'
    _order = 'status ASC'

    @api.constrains('status')
    def _check_status(self):
        for record in self:
            status = record.status

            duplicate_status = self.sudo().search(
                [('id', '!=', record.id), ('status', '=', status)])
            if duplicate_status:
                raise ValidationError(_("This Status has been used for another Config."))

    status = fields.Char(string='Status', required=True, index=True, trim=True)
    level_id = fields.Many2one('sale.order.line.level', string='Level', index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('status'):
                vals['status'] = vals.get('status').lower()
        return super().create(vals_list)


