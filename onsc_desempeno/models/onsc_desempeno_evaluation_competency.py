# -*- coding: utf-8 -*-
import logging

import html2text

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Borrador'),
    ('in_progress', 'En Proceso'),
    ('completed', 'Completado'),
    ('finished', 'Finalizado'),
    ('uncompleted', 'Sin Finalizar'),
    ('canceled', 'Cancelado')
]


class ONSCDesempenoEvaluationCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.competency'
    _description = u'Evaluación'


    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True)

    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo')
    improvement_areas = fields.Text(string='Brecha / Fortalezas / Aspectos a mejorar')
    skill_line_ids = fields.Many2many('onsc.desempeno.skill.line', 'skill_line_competency_rel', 'compentency_id', 'skill_line_id',
                                       string='Entorno')
    dimension_id = fields.Many2one('onsc.desempeno.dimension', string="Dimensión", readonly=True)
    behavior = fields.Char(string="Comportamiento esperado", readonly=True)

