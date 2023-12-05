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
    type = fields.Selection(SCORE_TYPE, string='Tipo', required=True, index=True)

    evaluations_qty = fields.Integer('Evaluaciones')
    finished_evaluations_qty = fields.Integer('Evaluaciones finalizadas')
    score = fields.Float('Puntaje')
    finished_score = fields.Float('Puntaje de Finalizados')
