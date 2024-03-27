from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class QCReceiveItem(models.Model):
    _name = 'qc.receive.item'
    _description = 'QC Receive Item'

    # @api.constrains('sale_order_line_id')
    # def _check_sale_order_line_id(self):
    #     for record in self:
    #         sale_order_line_id = record.sale_order_line_id
    #         if sale_order_line_id.sublevel_id.level != 'L4.1':
    #             raise ValidationError(_("Only Transfer Item With Production Level"))

    production_transfer_id = fields.Many2one('production.transfer', string='Production Transfer', required=True, index=True, ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', required=True, string='Item')
    production_id = fields.Char(string='Production ID', required=True, index=True)
    product_id = fields.Many2one('product.product', related='sale_order_line_id.product_id', store=True, index=True)
    product_template_attribute_value_ids = fields.Many2many(
        related='sale_order_line_id.product_template_attribute_value_ids')
    personalize = fields.Char(string='Personalize', related='sale_order_line_id.personalize', store=True)
    production_vendor_id = fields.Many2one('res.partner', string='Production Vendor',
                                           related='sale_order_line_id.production_vendor_id', store=True)
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level', related='sale_order_line_id.sublevel_id',
                                  store=True)
    address_sheft_id = fields.Many2one('fulfill.shelf', string='Address Shelf', related='sale_order_line_id.address_sheft_id',
                                       store=True)

    @api.onchange('production_id')
    def onchange_production_id(self):
        production_id = self.production_id
        if production_id:
            duplicate_items = self.production_transfer_id.qc_receive_item_ids.filtered(
                lambda item: item.production_id and item.production_id == production_id)
            if len(duplicate_items) > 1:
                raise ValidationError(_('Duplicate Production ID'))
            Items = self.env['sale.order.line'].sudo()
            item_id = Items.search([('production_id', '=', production_id)], limit=1)
            if item_id.sublevel_id.level != 'L4.1':
                raise ValidationError(_("Only Transfer Item With Production Level"))
            if item_id:
                self.sale_order_line_id = item_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if not val.get('sale_order_line_id'):
                vals_list.remove(val)
        res = super(QCReceiveItem, self).create(vals_list)
        transfer_ids = res.production_transfer_id
        remove_items = self
        for transfer in transfer_ids:
            total_received_items = transfer.qc_receive_item_ids
            production_ids = list(set(total_received_items.mapped('production_id')))
            for production in production_ids:
                lines = total_received_items.filtered(lambda line: line.production_id == production)
                if len(lines) > 1:
                    remove_items |= lines[1:]
        remove_items.unlink()
        return res