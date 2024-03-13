from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FulfillShelf(models.Model):
    _name = 'fulfill.shelf'
    _description = 'Shelf'
    _rec_name = 'shelf_name'

    shelf_code = fields.Char(string='Shelf Code')
    shelf_name = fields.Char(string='Shelf Name')
    shelf_type = fields.Many2one('fulfill.shelf.type', string='Shelf Type')

    @api.constrains('shelf_code')
    def _check_shelf_code(self):
        for record in self:
            shelf_code = record.shelf_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('shelf_code', '=', shelf_code)])
            if duplicate_code:
                raise ValidationError(_("This shelf code has been used for another shelf."))

    @api.model
    def action_generate_item_barcode_server(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        if any(not item.production_id for item in items):
            raise ValidationError('Could not generate barcode for None Production ID Item')
        return items.action_generate_item_barcode()

    def action_generate_item_barcode(self):
        try:
            data = []
            for rec in self:
                order_total_items = rec.order_id.order_line
                total_product_types = list(set(order_total_items.mapped('product_type')))
                product_str = f'{rec.address_sheft_id.shelf_code}'
                for product_type in total_product_types:
                    product_type_items = order_total_items.filtered(lambda item: item.product_type == product_type)
                    product_format = f'_{len(product_type_items)}{product_type}'
                    product_str += product_format
                data.append({
                    'shelf_code': rec.shelf_code,
                    'shelf_name': rec.shelf_name,
                })
            item_data = {
                'items': data
            }
            report = self.env.ref('crosify_order.action_generate_shelf_barcode')
            report_action = report.report_action(self, data=item_data, config=False)
            report_action.update({'close_on_report_download': True})
            return report_action

        except (ValueError, AttributeError):
            raise ValidationError('Cannot convert into barcode.')
