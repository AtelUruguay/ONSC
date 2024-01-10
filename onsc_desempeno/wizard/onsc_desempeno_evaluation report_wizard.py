# -*- coding: utf-8 -*-
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
    ('environment_consolidate', 'Consolidado de entorno'),]

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

    operating_unit_id = fields.Many2one('operating.unit', string='UE')
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar')
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', )
    state = fields.Selection(STATE, string='Estado', )
    gap_deal_state = fields.Selection(selection=GAP_DEAL_STATES,string="Subestado" )
    operating_unit_ids_domain = fields.Char(compute='_compute_operating_unit_ids_domain')

    @api.depends('state')
    def _compute_operating_unit_ids_domain(self):

        OperatingUnit = self.env['operating.unit'].suspend_security()
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        for rec in self:
            if self._is_group_admin_gh_inciso():
                operating_unit = OperatingUnit.suspend_security().search([('inciso_id', '=', inciso_id),])
                domain = [('id', 'not in', operating_unit.ids)]
            elif self._is_group_admin_gh_ue():
                 domain = [('id', '=', operating_unit_id)]
            else:
                domain = [('id', 'in', [])]
            rec.environment_ids_domain = json.dumps(domain)

    def action_show_org(self):
        inciso_withhistory = self.inciso_id.with_context(find_history=True, as_of_date=self.date)
        operating_unit_withhistory = self.operating_unit_id.with_context(find_history=True, as_of_date=self.date)
        if inciso_withhistory:
            inciso_name = inciso_withhistory.name_get()[0][1]
        else:
            inciso_name = self.inciso_id.name
        if operating_unit_withhistory:
            operating_unit_name = operating_unit_withhistory.name_search(
                args=[('id', '=', operating_unit_withhistory.id)])[0][1]
        else:
            operating_unit_name = self.operating_unit_id.name

        return {
            'type': 'ir.actions.client',
            'tag': 'organization_dashboard',
            'params': {
                'title': 'Organigrama',
                'operating_unit_id': self.operating_unit_id.id,
                'department_id': self.department_id.id,
                'short_name': self.short_name,
                'responsible': self.responsible,
                'end_date': self.date,
                'inciso': inciso_name or '',
                'ue': operating_unit_name or '',
            },
        }
