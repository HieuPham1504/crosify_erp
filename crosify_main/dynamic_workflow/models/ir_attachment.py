from odoo import api, fields, models

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        # res = super(IrAttachment, self)._search(domain, offset=0, limit=None, order=None, access_rights_uid=None)

        return super()._search(domain, offset, limit, order, access_rights_uid)

