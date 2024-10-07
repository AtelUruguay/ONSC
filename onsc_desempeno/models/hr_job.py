# -*- coding: utf-8 -*-

from odoo import models, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    def fields_get(self, allfields=None, attributes=None):
        res = super(HrJob, self).fields_get(allfields, attributes)
        if self._context.get('hide_custom_filters'):
            for field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
        return res

    evaluation_list_line_ids = fields.Many2many(
        comodel_name='onsc.desempeno.evaluation.list.line',
        ondelete="cascade",
        string='Líneas de evaluación de Lista de participantes')

    def create_job(
            self,
            contract,
            department,
            start_date,
            security_job,
            is_uo_manager=False,
            extra_security_roles=False,
            source_job=False
    ):
        new_job = super(HrJob, self).create_job(
            contract,
            department,
            start_date,
            security_job,
            is_uo_manager=is_uo_manager,
            extra_security_roles=extra_security_roles,
            source_job=source_job
        )
        if not self._context.get('ignore_evaluation_list_in', False):
            new_job.suspend_security()._update_evaluation_list_in(source_job=source_job)
        return new_job

    def deactivate(self, date_end):
        results = super(HrJob, self).deactivate(date_end)
        if not self._context.get('ignore_evaluation_list_out', False):
            for record in self:
                if self._context.get('is_copy_job'):
                    record.suspend_security()._update_evaluation_list_out_changejob()
                else:
                    record.suspend_security()._update_evaluation_list_out()
        return results

    def _update_evaluation_list_in(self, source_job=False):
        """
        0. soy responsable de mi puesto y soy nivel 1 no hago IN NOTA: Debe pasar a ser parte generica IDEM a escaladornes excluidos
        1. Si soy nuevo me tiene que meter en una lista de participantes
        2. Si tengo puesto origen y ya hay evaluaciones generadas para ese puesto origen no hago IN
        3. Si tengo puesto origen y no tengo evaluaciones debo meterme en una lista de participantes
        4. Si 3 y estoy en la lista de colaboradores sin evaluaciones eliminarme y volverme a subir para que quede apuntando al puesto vigente

        IN EN LISTA DE PARTICIPANTES
        Como saber en que UO debo adicionarme:
        Caso 1. 3. es en la UO del puesto nuevo o si soy lider en la UO padre

        :param source_job:
        :return:
        """
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        EvaluationList = self.env['onsc.desempeno.evaluation.list'].with_context(
            active_test=False,
            is_from_menu=False).suspend_security()
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security().with_context(ignore_security_rules=True)

        excluded_descriptor1_ids = self.env.company.descriptor1_ids.ids
        is_valid_contract = self.contract_id.legajo_state not in ['baja', 'reserved']
        manager = self.department_id.get_first_department_withmanager_in_tree().manager_id.id
        is_iam_manager = manager == self.employee_id.id
        case_0 = is_iam_manager and self.department_id.hierarchical_level_id.order == 1

        if is_valid_contract and self.contract_id.descriptor1_id.id not in excluded_descriptor1_ids and not case_0:
            # averiguando en que uo debo adicionarme como colaborador
            if is_iam_manager:
                _department = self.department_id.parent_id
            else:
                _department = self.department_id

            evaluation_lists = EvaluationList.search([
                ('state', '=', 'in_progress'),
                # se elimina restricción por movimientos de legajos anteriores a la fecha desde de la lista de participantes
                # ('evaluation_stage_id.start_date', '<=', self.start_date),
                ('evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.start_date),
                ('department_id', '=', _department.id),
            ])
            # new_evaluation_list_lines = EvaluationListLine
            for evaluation_list in evaluation_lists:
                if source_job:
                    source_job_evaluations = Evaluation.search_count([
                        ('current_job_id', '=', source_job.id),
                        ('create_date', '>=', source_job.start_date),
                        ('evaluation_stage_id', '=', evaluation_list.evaluation_stage_id.id),
                    ])
                else:
                    source_job_evaluations = 0
                my_collaborator_line = evaluation_list.with_context(active_test=True).line_ids.filtered(
                    lambda x: x.employee_id.id == self.employee_id.id)

                # ------------------- CASES MANAGER -----------------------------------
                # case_1 = not source_job
                case_2 = source_job and source_job_evaluations > 0
                case_3 = source_job and source_job_evaluations == 0
                case_4 = case_3 and len(my_collaborator_line) > 0
                # ------------------- CASES MANAGER -----------------------------------

                if case_2:
                    continue
                if case_4:
                    my_collaborator_line.unlink()

                EvaluationListLine.create({
                    'evaluation_list_id': evaluation_list.id,
                    'job_id': self.id,
                    'is_included': True
                })
            return

    def _is_evaluation_list_available(self, evaluation_list, source_job):
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].with_context(
            active_test=False,
            is_from_menu=False).suspend_security()
        if source_job:
            _date = source_job.end_date
            _department_id = source_job.department_id.id
            _job_id = source_job.id
        else:
            _date = self.start_date
            _department_id = self.department_id.id
            _job_id = self.id

        return EvaluationListLine.search_count([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', _date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', _date),
            ('evaluation_list_id.evaluation_stage_id', '=', evaluation_list.evaluation_stage_id.id),
            ('evaluation_list_id.department_id', '=', _department_id),
            ('job_id', '=', _job_id),
        ])

    def _update_evaluation_list_out(self):
        job_employee = self.employee_id
        EvaluationListLine = self.env['onsc.desempeno.evaluation.list.line'].suspend_security()
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security()
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        # SE DEPRECA EL FILTRO PARA EVITAR PROBLEMAS CON RESPONSABLE QUE APARECE COMO COLABORADOR EN LA LISTA PADRE
        # como ya Legajo le dio de baja en este momento deja de ser responsable y se pierde la forma de hace trace
        evaluation_list_lines = EvaluationListLine.with_context(active_test=False, is_from_menu=False).search([
            ('evaluation_list_id.state', '=', 'in_progress'),
            ('evaluation_list_id.evaluation_stage_id.start_date', '<=', self.end_date),
            ('evaluation_list_id.evaluation_stage_id.general_cycle_id.end_date_max', '>=', self.end_date),
            ('job_id', '=', self.id),
        ])
        Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', 'in',
             ['gap_deal', 'development_plan', 'tracing_plan', 'self_evaluation', 'environment_definition']),
            ('evaluated_id', '=', job_employee.id),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).action_cancel(is_canceled_by_employee_out=True)

        Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', 'in', ['leader_evaluation']),
            ('evaluated_id', '=', job_employee.id),
            ('current_job_id', '=', self.id),
            ('state', 'in', ['draft', 'in_process', 'completed', 'finished']),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
        ]).action_cancel(is_canceled_by_employee_out=True)

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
            ('evaluation_type', '=', 'collaborator'),
            ('current_job_id', '=', self.id),
            ('evaluation_stage_id.start_date', '<=', self.end_date),
            ('general_cycle_id.end_date_max', '>=', self.end_date),
            '|', ('evaluated_id', '=', job_employee.id), ('evaluator_id', '=', job_employee.id),
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

    def _update_evaluation_list_puente(self, source_job, target_job):
        # UTILITY: FORZAR CHECKOUT CHECK-IN DE DOS PUESTOS. TIENEN QUE ESTAR LOGICAMENTE RELACIONADOS
        source_job._update_evaluation_list_out_changejob()
        target_job._update_evaluation_list_in()

    def force_evaluation_out(self):
        self._update_evaluation_list_out()
