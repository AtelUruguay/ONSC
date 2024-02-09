# -*- coding:utf-8 -*-

from odoo import models


class ONSCLegajoCambioUO(models.Model):
    _inherit = 'onsc.legajo.cambio.uo'

    def _action_confirm(self):
        new_job = super(ONSCLegajoCambioUO, self)._action_confirm()
        # OBTENIENDO COLABORADORES
        evaluations = self.env['onsc.desempeno.evaluation'].with_context(ignore_security_rules=True).search([
            ('current_job_id', '=', self.job_id.id),
            ('create_date', '>=', self.job_id.start_date),
        ])
        self.env['onsc.desempeno.consolidated'].suspend_security().with_context(ignore_security_rules=True).search([
            ('current_job_id', '=', self.job_id.id),
            ('create_date', '>=', self.job_id.start_date),
        ]).write({'current_job_id': new_job.id})

        evaluations.write(
            {'current_job_id': new_job.id}
        )
        if len(evaluations) == 0:
            new_job._update_evaluation_list_in()
        return new_job

    def fix_evaluations(self):
        Job = self.env['hr.job'].sudo()
        for evaluation in self.env['onsc.desempeno.evaluation'].search([
            ('current_job_id', '=', False),
        ]):
            job = Job.search([
                ('employee_id', '=', evaluation.evaluated_id.id),
                ('department_id', '=', evaluation.uo_id.id)
            ], order="id desc", limit=1)
            evaluation.write({'current_job_id': job.id})
