from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ConfigSetLineLevel(models.Model):
    _name = 'config.set.line.level'
    _description = 'Config set line level'
    _rec_name = 'type'

    pre_set_shelf_ids = fields.Many2many(comodel_name='sale.order.line.level',
                                         relation='pre_config_level_order_line_level_rel',
                                         column1='config_level_id',
                                         column2='line_level_id',
                                         string='Pre shelf')
    set_shelf_ids = fields.Many2many(comodel_name='sale.order.line.level',
                                     relation='config_level_order_line_level_rel',
                                     column1='config_level_id',
                                     column2='line_level_id',
                                     string='Set shelf')
    post_set_shelf_ids = fields.Many2many(comodel_name='sale.order.line.level',
                                          relation='post_config_level_order_line_level_rel',
                                          column1='config_level_id',
                                          column2='line_level_id',
                                          string='Post shelf')

    type = fields.Selection([('shelf', "Shelf")], string="Type", required=True)

    _sql_constraints = [('type_uniq', 'unique(type)', "The Type must be unique.")]

    @api.onchange('type')
    def _onchange_type(self):
        record = self.sudo().search([('type', '=', self.type)], limit=1)
        if record:
            raise UserError("Type must be unique.")