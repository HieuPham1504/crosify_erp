from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FulfillShelf(models.Model):
    _name = 'fulfill.shelf'
    _description = 'Shelf'
    _rec_name = 'shelf_name'

    shelf_code = fields.Char(string='Shelf Code')
    shelf_name = fields.Char(string='Shelf Name')
    shelf_type = fields.Many2one('fulfill.shelf.type', string='Shelf Type')
    max_shelf = fields.Integer(string='Max Shelf', default=1)
    temp_shelf = fields.Integer(string='Temp Shelf', help='Temporary shelf')
    current_shelf = fields.Integer(string='Current Shelf')
    available = fields.Boolean(string='Available', compute='_compute_available', store=True)

    @api.constrains('shelf_code')
    def _check_shelf_code(self):
        for record in self:
            shelf_code = record.shelf_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('shelf_code', '=', shelf_code)])
            if duplicate_code:
                raise ValidationError(_("This shelf code has been used for another shelf."))

    @api.model
    def action_generate_shelf_barcode_server(self):
        item_ids = self._context.get('active_ids', [])
        items = self.sudo().search([('id', 'in', item_ids)], order='id asc')
        return items.action_generate_shelf_barcode()

    def action_generate_shelf_barcode(self):
        try:
            data = []
            for rec in self:
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

    @api.depends('current_shelf', 'max_shelf', 'temp_shelf')
    def _compute_available(self):
        for record in self:
            if record.temp_shelf >= record.max_shelf or record.current_shelf >= record.max_shelf:
                record.available = False
            else:
                record.available = True

    @api.model
    def action_compute_current_shelf(self):
        item_ids = self._context.get('active_ids', [])
        records = self.sudo().search([('id', 'in', item_ids)])
        config_set_line_level_id = self.env['config.set.line.level'].sudo().search([('type', '=', 'shelf')], limit=1)
        if config_set_line_level_id:
            level_ids = config_set_line_level_id.set_shelf_ids.ids
        else:
            level_ids = []
        for rec in records:
            count_shelf = self.env['sale.order.line'].sudo().search_count([('address_sheft_id', '=', rec.id),
                                                                           ('sublevel_id', 'in', level_ids)])
            rec.current_shelf = count_shelf

    @api.model
    def action_compute_temp_shelf(self):
        item_ids = self._context.get('active_ids', [])
        records = self.sudo().search([('id', 'in', item_ids)])
        config_set_line_level_id = self.env['config.set.line.level'].sudo().search([('type', '=', 'shelf')], limit=1)
        if config_set_line_level_id:
            set_shelf_ids = config_set_line_level_id.set_shelf_ids.ids
            pre_set_shelf_ids = config_set_line_level_id.pre_set_shelf_ids.ids
            level_ids = set_shelf_ids + pre_set_shelf_ids
        else:
            level_ids = []
        for rec in records:
            count_shelf = self.env['sale.order.line'].sudo().search_count([('address_sheft_id', '=', rec.id),
                                                                           ('sublevel_id', 'in', level_ids)])
            rec.temp_shelf = count_shelf
