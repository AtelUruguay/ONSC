# -*- coding: utf-8 -*-

from odoo import models, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    evaluation_list_line_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list.line',
        ondelete="set null",
        string='Línea de evaluación de Lista de participantes')

    def create_job(self, contract, department, start_date, security_job, extra_security_roles=False,
                   is_job_change=False):
        new_job = super(HrJob, self).create_job(
            contract,
            department,
            start_date,
            security_job,
            extra_security_roles=extra_security_roles,
            is_job_change=is_job_change
        )
        if not is_job_change:
            new_job._update_evaluation_list_in()
        return new_job

    def deactivate(self, date_end, is_job_change=False):
        results = super(HrJob, self).deactivate(date_end)
        for record in self:
            if not is_job_change:
                record._update_evaluation_list_out()
            else:
                record._update_evaluation_list_out_changejob()
        return results

    def _update_evaluation_list_in(self):
        exluded_descriptor1_ids = self.env.company.descriptor1_ids.ids
        is_valid_contract = self.contract_id.legajo_state not in ['baja', 'reserved']
        if is_valid_contract and self.contract_id.descriptor1_id not in exluded_descriptor1_ids:
            EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()

            manager = self.department_id.get_first_department_withmanager_in_tree().manager_id
            parent_manager = self.department_id.parent_id.get_first_department_withmanager_in_tree().manager_id
            eval1 = not (self.department_id.hierarchical_level_id.order == 1
                         and self.department_id.manager_id.id == self.employee_id.id)
            eval2 = self.employee_id.id != manager.id
            if eval1 and eval2:
                _department = self.department_id
            elif eval1 and not eval2 and self.department_id.parent_id.id and \
                    parent_manager.id != self.employee_id.id:
                _department = self.department_id.parent_id
            evaluation_list_lines = EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
                ('evaluation_list_id.state', '=', 'in_progress'),
                ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.start_date),
                ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.start_date),
                ('evaluation_list_id.department_id', '=', _department.id),
            ])
            evaluation_employees = evaluation_list_lines.mapped('employee_id')
            if len(evaluation_list_lines) and self.employee_id not in evaluation_employees.ids:
                new_evaluation_list_line = EvaluationListLine.create({
                    'evaluation_list_id': evaluation_list_lines[0].evaluation_list_id.id,
                    'job_id': self.id,
                    'is_included': True
                })
                self.write({'evaluation_list_line_id': new_evaluation_list_line.id})
        return True

    def _update_evaluation_list_in_changejob(self, base_job):
        """
        :param base_job: Recordset de hr.job: Puesto origen
        :return:
        """
        if self.contract_id.legajo_state not in ['baja', 'reserved']:
            EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
            evaluation_list_lines = EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
                ('evaluation_list_id.state', '=', 'in_progress'),
                ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.start_date),
                ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.start_date),
                ('evaluation_list_id.department_id', '=', self.department_id.id),
            ])
            evaluation_employees = evaluation_list_lines.mapped('employee_id')
            if len(evaluation_list_lines) and self.employee_id not in evaluation_employees.ids:
                new_evaluation_list_line = EvaluationListLine.create({
                    'evaluation_list_id': evaluation_list_lines[0].evaluation_list_id.id,
                    'job_id': self.id,
                    'is_included': False
                })
                self.write({'evaluation_list_line_id': new_evaluation_list_line.id})
        return True

    def _update_evaluation_list_out(self):
        job_employee = self.employee_id
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security()
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        evaluation_list_lines = EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.end_date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.end_date),
            ('evaluation_list_id.department_id', '=', self.department_id.id),
            ('job_id', '=', self.id),
        ])
        for evaluation in evaluation_list_lines.mapped('evaluation_ids'):
            if evaluation.evaluation_type in ['self_evaluation', 'environment_definition', 'collaborator']:
                evaluation.action_cancel(is_canceled_by_employee_out=True)
            elif evaluation.evaluation_type in ['environment_evaluation']:
                if evaluation.evaluated_id == job_employee:
                    evaluation.action_cancel(is_canceled_by_employee_out=True)
                elif evaluation.evaluator_id == job_employee and evaluation.state in ['draft', 'in_process']:
                    evaluation.action_cancel(is_canceled_by_employee_out=True)
            elif evaluation.evaluation_type in ['leader_evaluation']:
                if evaluation.evaluated_id == job_employee and evaluation.state in ['draft', 'in_process', 'completed',
                                                                                    'finished']:
                    evaluation.action_cancel(is_canceled_by_employee_out=True)

        Consolidated.with_context(ignore_security_rules=True).search([
            ('evaluated_id', '=', job_employee.id),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).write({'active': False})

        # EVALUACION DE ENTORNO
        Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', '=', 'environment_evaluation'),
            ('evaluated_id', '=', job_employee.id),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).action_cancel(is_canceled_by_employee_out=True)

        Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', '=', 'environment_evaluation'),
            ('evaluator_id', '=', job_employee.id),
            ('state', 'in', ['draft', 'in_process']),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).action_cancel(is_canceled_by_employee_out=True)
        # FIN EVALUACION DE ENTORNO
        Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', 'in', ['gap_deal', 'development_plan', 'tracing_plan']),
            ('evaluated_id', '=', job_employee.id),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).action_cancel(is_canceled_by_employee_out=True)

        Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', '=', 'collaborator'),
            ('evaluated_id', '=', job_employee.id),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).action_cancel(is_canceled_by_employee_out=True)

        evaluation_list_lines.filtered(lambda x: x.state != 'generated').unlink()

    def _update_evaluation_list_out_changejob(self):
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.end_date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.end_date),
            ('evaluation_list_id.department_id', '=', self.department_id.id),
            ('state', '!=', 'generated'),
            ('job_id', '=', self.id),
        ]).unlink()

    def force_evaluation_out(self):
        self._update_evaluation_list_out()
