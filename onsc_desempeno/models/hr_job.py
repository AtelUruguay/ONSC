# -*- coding: utf-8 -*-

from odoo import models, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    @api.model
    def create(self, vals):
        record = super(HrJob, self).create(vals)
        return record

    def _update_evaluation_list(self):
        if self.contrato_id.legajo_state in ['active', 'incoming_commission']:
            EvaluationList = self.env['onsc.desempeno.evaluation.list'].suspend_security()
            evaluation_list = EvaluationList.search([
                ('state', '=', 'in_progress'),
                ('department_id', '=', self.department_id.id),
            ], limit=1)
            evaluation_employees = evaluation_list.line_ids.mapped('employee_id')
            evaluation_employees |= evaluation_list.evaluation_generated_line_ids.filtered(
                lambda x: x.state == 'generated').mapped('employee_id')
            if self.employee_id not in evaluation_employees.ids:
                evaluation_list.write({0, 0, {
                    'job_id': self.id,
                }})
        return True
