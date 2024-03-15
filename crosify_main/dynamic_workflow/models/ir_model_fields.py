from odoo import api, models, fields, _


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    is_dynamic = fields.Boolean(string="Dynamic Field")
    stage_id = fields.Many2one('dynamic.workflow.stage')
    is_required = fields.Boolean('Bắt buộc')
    dynamic_view = fields.Many2one('ir.ui.view')

    def unlink(self):
        for rec in self:
            if rec.dynamic_view:
                rec.dynamic_view.unlink()
        return super(IrModelFields, self).unlink()

    @api.constrains('is_required')
    def _onchange_is_required(self):
        view = self.dynamic_view.arch_base
        if view:
            if self.is_required:
                self.sudo().dynamic_view.arch_base = view.replace('color-default',
                                                                  'color-required')
            else:
                self.sudo().dynamic_view.arch_base = view.replace('color-required',
                                                                  'color-default')
