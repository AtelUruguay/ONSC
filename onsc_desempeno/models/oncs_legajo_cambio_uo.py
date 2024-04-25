# -*- coding:utf-8 -*-

from odoo import models


class ONSCLegajoCambioUO(models.Model):
    _inherit = 'onsc.legajo.cambio.uo'

    def _action_confirm(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security()
        new_job = super(ONSCLegajoCambioUO, self)._action_confirm()
        # FIXME en LED no es obligatorio que se haga un nuevo puesto
        if new_job:
            # OBTENIENDO COLABORADORES
            Evaluation.with_context(ignore_security_rules=True).search([
                ('current_job_id', '=', self.job_id.id),
                ('create_date', '>=', self.job_id.start_date),
            ]).write({'current_job_id': new_job.id})
            Evaluation.with_context(ignore_security_rules=True).search([
                ('evaluator_current_job_id', '=', self.job_id.id),
                ('create_date', '>=', self.job_id.start_date),
            ]).write({'evaluator_current_job_id': new_job.id})
            Consolidated.with_context(ignore_security_rules=True).search([
                ('current_job_id', '=', self.job_id.id),
                ('create_date', '>=', self.job_id.start_date),
            ]).write({'current_job_id': new_job.id})
        return new_job

    def fix_evaluations(self):
        Job = self.env['hr.job'].sudo()
        for evaluation in self.env['onsc.desempeno.evaluation'].sudo().search([
            ('current_job_id', '=', False),
        ]):
            job = Job.search([
                ('employee_id', '=', evaluation.evaluated_id.id),
                ('department_id', '=', evaluation.uo_id.id)
            ], order="id desc", limit=1)
            evaluation.sudo().write({'current_job_id': job.id})
