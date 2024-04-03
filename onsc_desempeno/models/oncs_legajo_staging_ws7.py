# -*- coding: utf-8 -*-

from odoo import models


class ONSCLegajoStagingWS7(models.Model):
    _inherit = 'onsc.legajo.staging.ws7'

    def set_asc_transf_reest(self, Contract, record):
        if record.mov == 'ASCENSO':
            _self = self.with_context(is_copy_job=True)
            Contract = Contract.with_context(is_copy_job=True)
            record = record.with_context(is_copy_job=True)
        else:
            _self = self.with_context(is_copy_job=True)
            Contract = Contract.with_context(is_copy_job=True)
            record = record.with_context(is_copy_job=True)

        super(ONSCLegajoStagingWS7, _self).set_asc_transf_reest(Contract, record)

    def _copy_jobs_update_new_job_data(self, source_job, new_job):
        super(ONSCLegajoStagingWS7, self)._copy_jobs_update_new_job_data(source_job, new_job)
        # if self._context.get('is_same_uo'):
        #     self.env['hr.job']._update_evaluation_list_puente(source_job, new_job)
        if self._context.get('ignore_evaluation_list_in') and self._context.get('ignore_evaluation_list_out'):
            return

        # A LAS EVALUACIONES LES ASIGNA EL NUEVO PUESTO AL CURRENT JOB
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security().with_context(ignore_security_rules=True)
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security().with_context(
            ignore_security_rules=True)

        Evaluation.search([
            ('current_job_id', '=', source_job.id),
            ('create_date', '>=', source_job.start_date),
        ]).write(
            {'current_job_id': new_job.id}
        )
        Consolidated.search([
            ('current_job_id', '=', source_job.id),
            ('create_date', '>=', source_job.start_date),
        ]).write({'current_job_id': new_job.id})

        # evaluations.write(
        #     {'current_job_id': new_job.id}
        # )
        # if len(evaluations) == 0 and not self._context.get('ignore_evaluation_list_in'):
        #     new_job._update_evaluation_list_in()

        return True

    def _check_contract_data(self, contract):
        super(ONSCLegajoStagingWS7, self)._check_contract_data(contract)
        for job_id in contract.job_ids:
            job_id.with_context(is_copy_job=False)._update_evaluation_list_in()
        return True
