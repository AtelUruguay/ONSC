# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

SCORE_TYPE = [
    ('eval_360', 'Evaluación 360'),
]


class ONSCDesempenoScore(models.Model):
    _name = 'onsc.desempeno.score'
    _description = u'Desempeño - Puntajes'

    evaluation_stage_id = fields.Many2one(
        'onsc.desempeno.evaluation.stage',
        string='Evaluación 360')
    evaluation_list_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list',
        string='Lista de participantes')
    department_id = fields.Many2one(
        "hr.department",
        string="Unidad organizativa",
        required=True,
        index=True)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Evaluado",
        store=True,
        index=True)

    evaluations_360_total_qty = fields.Integer('Evaluaciones 360')
    evaluations_360_finished_qty = fields.Integer('Evaluaciones 360 finalizadas')
    evaluations_360_score = fields.Float('Puntaje 360 base')
    evaluations_360_finished_score = fields.Float('Puntaje 360')
    evaluations_gap_deal_finished_score = fields.Float('Puntaje Acuerdo de brecha')
    evaluations_tracing_plan_finished_score = fields.Float('Puntaje Seguimiento del Plan de desarrollo')
    score = fields.Float('Puntaje final')



