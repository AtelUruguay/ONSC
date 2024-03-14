# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCLegajoStagingWS7(models.Model):
    _inherit = 'onsc.legajo.staging.ws7'

    def set_asc_transf_reest(self, Contract, record):
        if record.mov == 'ASCENSO':
            _self = self.with_context(ignore_evaluation_list_in=True, ignore_evaluation_list_out=True)
            Contract = Contract.with_context(ignore_evaluation_list_in=True, ignore_evaluation_list_out=True)
            record = record.with_context(ignore_evaluation_list_in=True, ignore_evaluation_list_out=True)
        else:
            _self = self.with_context(ignore_evaluation_list_in=True, ignore_evaluation_list_out=True, is_same_uo=True)
            Contract = Contract.with_context(ignore_evaluation_list_in=True, ignore_evaluation_list_out=True,
                                         is_same_uo=True)
            record = record.with_context(ignore_evaluation_list_in=True, ignore_evaluation_list_out=True, is_same_uo=True)

        return super(ONSCLegajoStagingWS7, _self).set_asc_transf_reest(Contract, record)


    def _copy_jobs_update_new_job_data(self, source_job, new_job):
        super(ONSCLegajoStagingWS7, self)._copy_jobs_update_new_job_data(source_job, new_job)

        if self._context.get('is_same_uo'):
            self.env['hr.job']._update_evaluation_list_puente(source_job, new_job)

        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security().with_context(ignore_security_rules=True)
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security().with_context(
            ignore_security_rules=True)

        evaluations = Evaluation.search([
            ('current_job_id', '=', source_job.id),
            ('create_date', '>=', source_job.start_date),
        ])
        Consolidated.search([
            ('current_job_id', '=', source_job.id),
            ('create_date', '>=', source_job.start_date),
        ]).write({'current_job_id': new_job.id})

        evaluations.write(
            {'current_job_id': new_job.id}
        )
        if len(evaluations) == 0:
            new_job._update_evaluation_list_in()

        return True
