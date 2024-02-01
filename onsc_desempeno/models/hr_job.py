# -*- coding: utf-8 -*-

from odoo import models, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    evaluation_list_line_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list.line',
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
        else:
            new_job._update_evaluation_list_in_changejob()
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
                    'job_id': self.id
                })
                self.write({'evaluation_list_line_id': new_evaluation_list_line.id})
        return True

    def _update_evaluation_list_in_changejob(self):
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
                    'job_id': self.id
                })
                self.write({'evaluation_list_line_id': new_evaluation_list_line.id})
        return True

    def _update_evaluation_list_out(self):
        user_employee = self.env.user.employee_id
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security()
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        evaluation_list_lines = EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.start_date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.start_date),
            ('evaluation_list_id.department_id', '=', self.department_id.id),
            ('job_id', '=', self.id),
        ])
        for evaluation in evaluation_list_lines.mapped('evaluation_ids'):
            if evaluation.type in ['self_evaluation', 'environment_definition', 'collaborator']:
                evaluation.button_cancel()
            elif evaluation.type in ['environment_evaluation']:
                if evaluation.evaluated_id == user_employee:
                    evaluation.button_cancel()
                elif evaluation.evaluator_id == user_employee and evaluation.state in ['draft', 'in_process']:
                    evaluation.button_cancel()
            elif evaluation.type in ['leader_evaluation']:
                if evaluation.evaluated_id == user_employee and evaluation.state in ['draft', 'in_process', 'completed',
                                                                                     'finished']:
                    evaluation.button_cancel()

        Consolidated.search([
            ('evaluated_id', '=', user_employee.id),
            ('uo_id', '=', self.department_id.id),
            ('evaluation_stage_id.start_date', '<=', self.start_date),
            ('general_cycle_id.end_date_max', '>=', self.start_date),
        ]).write({'active': False})

        Evaluation.search([
            ('evaluation_type', 'in', ['gap_deal', 'development_plan', 'tracing_plan']),
            ('evaluated_id', '=', user_employee.id),
            ('uo_id', '=', self.department_id.id),
            ('evaluation_stage_id.start_date', '<=', self.start_date),
            ('general_cycle_id.end_date_max', '>=', self.start_date),
        ]).button_cancel()

        evaluation_list_lines.filtered(lambda x: x.state != 'generated').unlink()

    def _update_evaluation_list_out_changejob(self):
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.start_date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.start_date),
            ('evaluation_list_id.department_id', '=', self.department_id.id),
            ('state', '=', 'generated'),
            ('job_id', '=', self.id),
        ]).unlink()
