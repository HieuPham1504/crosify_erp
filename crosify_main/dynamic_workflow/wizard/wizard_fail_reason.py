from odoo import api, fields, models


class WizardFailReason(models.TransientModel):
    _name = 'wizard.fail.reason'

    task_id = fields.Many2one('dynamic.workflow.task')
    fail_reason_ids = fields.Many2many('fail.reason', compute='_compute_fail_reason_ids')
    fail_reason = fields.Many2one('fail.reason', 'Lí do thất bại')

    @api.depends('task_id')
    def _compute_fail_reason_ids(self):
        for rec in self:
            rec.fail_reason_ids = rec.task_id.workflow_id.fail_reason_ids

    def action_confirm(self):
        fail_stage = self.task_id.workflow_id.stage_ids.filtered(lambda r: r.is_fail_stage)
        self.task_id.write({
            'fail_reason': self.fail_reason.name,
            'stage_id': fail_stage.id
        })
