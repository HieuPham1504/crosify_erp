from odoo import api, fields, models


class AssignTask(models.TransientModel):
    _name = 'assign.task'

    work_by_id = fields.Many2one('res.users', 'Người nhận việc', required=True)
    stage_id = fields.Many2one('dynamic.workflow.stage')
    task_id = fields.Many2one('dynamic.workflow.task')
    work_by_domain = fields.Many2many('res.users', compute='_compute_domain_work_by')

    @api.depends('stage_id')
    def _compute_domain_work_by(self):
        for rec in self:
            rec.work_by_domain = rec.stage_id.work_by_ids

    def action_confirm(self):
        self.task_id.write({
            'work_by_id': self.work_by_id.id,
            'stage_id': self.stage_id.id,
        })
