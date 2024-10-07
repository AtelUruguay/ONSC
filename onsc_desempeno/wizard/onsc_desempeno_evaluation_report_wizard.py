# -*- coding: utf-8 -*-
# pylint: disable=E8102
# pylint: disable=E8103
import json

from odoo import fields, models, api

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_definition', 'Definición de entorno'),
    ('gap_deal', 'Acuerdo de Brecha'),
    ('development_plan', 'Plan de desarrollo'),
    ('tracing_plan', 'Seguimiento del Plan de desarrollo'),
    ('collaborator_consolidate', 'Consolidado de colaborador'),
    ('environment_consolidate', 'Consolidado de entorno'), ]

STATE = [
    ('draft', 'Borrador'),
    ('in_process', 'En Proceso'),
    ('completed', 'Completado'),
    ('deal_close', "Acuerdo cerrado"),
    ('agreed_plan', "Plan Acordado"),
    ('uncompleted', 'Sin Finalizar'),
    ('finished', 'Finalizado'),
    ('canceled', 'Cancelado')
]

GAP_DEAL_STATES = [
    ('no_deal', 'Pendiente'),
    ('agree_leader', 'Acordado Líder'),
    ('agree_evaluated', 'Acordado Evaluado'),
    ('agree', 'Acordado'),
]


class ONSCOrganizationalWizard(models.TransientModel):
    _name = 'onsc.desempeno.evaluation.report.wizard'
    _description = 'Consulta General del Ciclo de Evaluación'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.employee_id.job_id.contract_id.operating_unit_id.id

    @api.model
    def _default_inciso(self):
        return self.env.user.employee_id.job_id.contract_id.inciso_id.id

    @api.model
    def _default_general_cycle(self):
        year = fields.Date.today().strftime('%Y')
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        general_cycle_id = GeneralCycle.search([('year', '=', year)], limit=1)
        return general_cycle_id.id

    @api.onchange("inciso_id")
    def _onchange_inciso_id(self):

        if self._is_group_admin():
            if self.inciso_id and self.inciso_id.id == self.env.user.employee_id.job_id.contract_id.inciso_id.id:
                self.operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
            else:
                self.operating_unit_id = False

    def _is_group_desempeno_admin_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso')

    def _is_group_desempeno_admin_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue')

    def _is_group_admin(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_administrador')

    operating_unit_id = fields.Many2one('operating.unit', string='UE',
                                        default=lambda self: self._default_operating_unit())
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar',
                                       default=lambda self: self._default_general_cycle())
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', )
    state = fields.Selection(STATE, string='Estado', )
    operating_unit_ids_domain = fields.Char(compute='_compute_operating_unit_ids_domain')
    operating_unit_edit = fields.Boolean('Puede editar el form?', compute='_compute_operating_unit_edit')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', default=lambda self: self._default_inciso())
    inciso_edit = fields.Boolean('Puede editar el form?', compute='_compute_inciso_edit')
    inciso_ids_domain = fields.Char(compute='_compute_inciso_ids_domain')

    @api.depends('inciso_id')
    def _compute_operating_unit_ids_domain(self):

        OperatingUnit = self.env['operating.unit'].suspend_security()
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        for rec in self:
            if self._is_group_desempeno_admin_gh_inciso():
                if rec.inciso_id:
                    operating_unit = OperatingUnit.suspend_security().search([('inciso_id', '=', rec.inciso_id.id), ])
                    domain = [('id', 'in', operating_unit.ids)]
                else:
                    domain = [('id', '=', False)]
            elif self._is_group_desempeno_admin_gh_ue():
                domain = [('id', '=', operating_unit_id)]
            else:
                if rec.inciso_id:
                    operating_unit = OperatingUnit.suspend_security().search([('inciso_id', '=', rec.inciso_id.id), ])
                    domain = [('id', 'in', operating_unit.ids)]
                else:
                    domain = [('id', 'in', [])]
            rec.operating_unit_ids_domain = json.dumps(domain)

    @api.depends('operating_unit_id')
    def _compute_operating_unit_edit(self):
        for rec in self:
            if self._is_group_desempeno_admin_gh_inciso() or self._is_group_admin():
                rec.operating_unit_edit = True
            else:
                rec.operating_unit_edit = False

    @api.depends('inciso_id')
    def _compute_inciso_edit(self):
        for rec in self:
            if self._is_group_admin():
                rec.inciso_edit = True
            else:
                rec.inciso_edit = False

    @api.depends('state')
    def _compute_inciso_ids_domain(self):

        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        for rec in self:
            if self._is_group_desempeno_admin_gh_inciso() or self._is_group_desempeno_admin_gh_ue():
                domain = [('id', '=', inciso_id)]
            else:
                domain = []
            rec.inciso_ids_domain = json.dumps(domain)

    def action_show_report(self):
        where_clause = []

        _where = ""
        if self.inciso_id:
            where_clause.append(" inciso_id = '%s' " % str(self.inciso_id.id))
        if self.operating_unit_id:
            where_clause.append(" operating_unit_id = '%s' " % str(self.operating_unit_id.id))

        if self.general_cycle_id:
            where_clause.append(" general_cycle_id = '%s' " % str(self.general_cycle_id.id))

        if self.evaluation_type:
            where_clause.append(" evaluation_type = '%s' " % self.evaluation_type)

        if self.state:
            where_clause = " AND ".join(where_clause)
            _where = "where  evaluation_type not in ('gap_deal','development_plan') and state = '%s' and " % self.state + where_clause
            _where_gap_deal = "where  evaluation_type in ('gap_deal','development_plan') and state_gap_deal = '%s' and " % self.state + where_clause
            _query = """INSERT INTO onsc_desempeno_evaluation_report(operating_unit_id, general_cycle_id, evaluation_type,
                                state, gap_deal_state, evaluated_id, evaluator_id, user_id,evaluation_id,inciso_id)
                            SELECT operating_unit_id, general_cycle_id, evaluation_type, state, gap_deal_state,
                            evaluated_id, evaluator_id, %s as user_id,id,inciso_id
                            FROM onsc_desempeno_evaluation %s
                            UNION
                            SELECT operating_unit_id, general_cycle_id, evaluation_type, state_gap_deal, gap_deal_state,
                            evaluated_id, evaluator_id, %s as user_id,id,inciso_id
                            FROM onsc_desempeno_evaluation %s""" % (
                self.env.user.id, _where, self.env.user.id, _where_gap_deal)
            cr = self.env.cr
            cr.execute("DELETE FROM onsc_desempeno_evaluation_report WHERE user_id = '%s'" % self.env.user.id)
            cr.execute(_query)

        else:
            if where_clause:
                where_clause = " AND ".join(where_clause)
            where_consolidate = where_clause
            if self.evaluation_type and self.evaluation_type == 'environment_consolidate':
                where_consolidate = where_consolidate.replace('environment_consolidate', 'environment')
            elif self.evaluation_type and self.evaluation_type == 'collaborator_consolidate':
                where_consolidate = where_consolidate.replace('collaborator_consolidate', 'collaborator')

            _query = """INSERT INTO onsc_desempeno_evaluation_report(operating_unit_id, general_cycle_id, evaluation_type,
                                state, gap_deal_state, evaluated_id, evaluator_id, user_id,evaluation_id, consolidated_id,inciso_id)
                            SELECT operating_unit_id, general_cycle_id, evaluation_type,
                            CASE
                                WHEN evaluation_type in ('gap_deal','development_plan') THEN state_gap_deal
                                WHEN  evaluation_type not in ('gap_deal','development_plan') THEN state
                            END AS state,
                            gap_deal_state,
                            evaluated_id, evaluator_id, %s as user_id,id,NULL,inciso_id
                            FROM onsc_desempeno_evaluation  WHERE %s
                            UNION
                            SELECT operating_unit_id, general_cycle_id,
                            CASE
                                WHEN evaluation_type = 'environment' THEN 'environment_consolidate'
                                WHEN  evaluation_type = 'collaborator' THEN 'collaborator_consolidate'
                            END AS evaluation_type, '','', evaluated_id, hr_employee_id as evaluator_id, %s as user_id,
                            NULL,id,inciso_id
                            FROM onsc_desempeno_consolidated cons
                            INNER JOIN hr_employee_onsc_desempeno_consolidated_rel rel
                            ON cons.id = rel.onsc_desempeno_consolidated_id WHERE %s""" % (
                self.env.user.id, where_clause or "TRUE", self.env.user.id, where_consolidate or "TRUE")

        cr = self.env.cr
        cr.execute("DELETE FROM onsc_desempeno_evaluation_report WHERE user_id = '%s'" % self.env.user.id)
        cr.execute(_query)
        action = self.env.ref('onsc_desempeno.action_onsc_desempeno_evaluation_report').suspend_security().read()[0]
        action['target'] = 'main'
        return action
