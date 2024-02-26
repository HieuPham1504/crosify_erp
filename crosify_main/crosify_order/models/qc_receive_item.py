from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class QCReceiveItem(models.Model):
    _name = 'qc.receive.item'
    _description = 'QC Receive Item'

    @api.constrains('sale_order_line_id')
    def _check_sale_order_line_id(self):
        for record in self:
            sale_order_line_id = record.sale_order_line_id
            if sale_order_line_id.sublevel_id.level != 'L4.1':
                raise ValidationError(_("Only Transfer Item With Production Level"))

    production_transfer_id = fields.Many2one('production.transfer', string='Production Transfer', required=True, index=True)
    sale_order_line_id = fields.Many2one('sale.order.line', required=True, string='Item')
    production_id = fields.Char(string='Production ID', required=True, index=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', store=True, index=True)
    product_template_attribute_value_ids = fields.Many2many(
        related='sale_order_line_id.product_template_attribute_value_ids')
    personalize = fields.Char(string='Personalize', related='sale_order_line_id.personalize', store=True)

    @api.onchange('production_id')
    def onchange_production_id(self):
        production_id = self.production_id
        if production_id:
            Items = self.env['sale.order.line'].sudo()
            item_id = Items.search([('production_id', '=', production_id)], limit=1)
            if item_id.sublevel_id.level != 'L4.1':
                raise ValidationError(_("Only Transfer Item With Production Level"))
            if item_id:
                self.sale_order_line_id = item_id.id