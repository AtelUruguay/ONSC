# -*- coding: utf-8 -*-
from odoo import fields, models

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


class ONSCDesempenoEvaluationReport(models.Model):
    _name = "onsc.desempeno.evaluation.report"
    _description = "Reporte y Consulta General de Ciclo de Evaluación "

    operating_unit_id = fields.Many2one('operating.unit', string='UE')
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar')
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', )
    state = fields.Selection(STATE, string='Estado', )
    gap_deal_state = fields.Selection(selection=GAP_DEAL_STATES, string="Subestado")
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado')
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador')
    user_id = fields.Many2one('res.users', string='Usuario', readonly=True)
    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación')
    consolidated_id = fields.Many2one('onsc.desempeno.consolidated', string='Consolidado')

    def button_open_evaluation(self):
        ctx = self.env.context.copy()

        if self.evaluation_type in ('collaborator_consolidate', 'environment_consolidate'):
            ctx.update({'readonly_evaluation': True})
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_collaborator_consolidated_readonly_action').read()[0]
            action.update({'res_id': self.consolidated_id.id, 'context': ctx, })
            return action
        else:
            ctx.update({'readonly_evaluation': True})
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_readonly_action').read()[0]
            action.update({'res_id': self.evaluation_id.id, 'context': ctx, })
            return action
