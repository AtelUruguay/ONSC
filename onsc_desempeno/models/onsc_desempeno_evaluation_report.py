# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api
from odoo.osv import expression

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
class ONSCDesempenoEvaluationReport(models.Model):
    _name = "onsc.desempeno.evaluation.report"
    _description = "Reporte y Consulta General de Ciclo de Evaluación "

    def _is_group_usuario_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_usuario_gh_inciso')

    def _is_group_usuario_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_usuario_gh_ue')
    def _is_group_admin(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_administrador')

    operating_unit_id = fields.Many2one('operating.unit', string='UE')
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar')
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', )
    state = fields.Selection(STATE, string='Estado', )
    gap_deal_state = fields.Selection(selection=GAP_DEAL_STATES,string="Subestado")
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado')
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador')

