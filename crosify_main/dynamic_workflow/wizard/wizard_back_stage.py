from odoo import api, fields, models


class BackStage(models.TransientModel):
    _name = 'back.stage'

    stage_id = fields.Many2one('dynamic.workflow.stage')
    task_id = fields.Many2one('dynamic.workflow.task')
    back_stage_ids = fields.Many2many('dynamic.workflow.stage', compute='_compute_domain_back_stage')
    back_stage_id = fields.Many2one('dynamic.workflow.stage', string='Giai đoạn kéo về', required=True)

    @api.depends('stage_id')
    def _compute_domain_back_stage(self):
        for rec in self:
            if rec.stage_id.type_back_stage == 'specifically':
                rec.back_stage_ids = rec.stage_id.back_stage_ids
            else:
                rec.back_stage_ids = self.env['dynamic.workflow.stage'].sudo().search([('workflow_id', '=', rec.stage_id.workflow_id.id),
                                                                                       ('id', '!=', rec.stage_id.id),
                                                                                       ('sequence', '<', rec.stage_id.sequence),
                                                                                       ('is_done_stage', '=', False),
                                                                                       ('is_fail_stage', '=', False)])

    def action_confirm(self):
        stage_process = self.task_id.task_process.filtered(lambda r: r.stage_id == self.back_stage_id)
        self.task_id.write({
            'stage_id': self.back_stage_id.id,
            'work_by_id': stage_process.work_by_id.id
        })
