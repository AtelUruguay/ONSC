# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Borrador'),
    ('in_progress', 'En Proceso'),
    ('completed', 'Completado'),
    ('finished', 'Finalizado'),
    ('uncompleted', 'Sin Finalizar'),
    ('canceled', 'Cancelado')
]

class ONSCDesempenoEvaluationCompentency(models.Model):
    _name = 'onsc.desempeno.evaluation.compentency'
    _description = u'Evaluación'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado',related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True)
    dimension_id = fields.Many2one('onsc.desempeno.dimension', string='Dimensión', readonly=True)
    expected_behavior = fields.Text(string='Comportamiento Esperado', readonly=True)
    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo', readonly=True,
                                states={'in_progress': [('readonly', False)]})
    improvement_areas = fields.Text(string='Brecha / Fortalezas / Aspectos a mejorar', readonly=True,
                                    states={'in_progress': [('readonly', False)]})
