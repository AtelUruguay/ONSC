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


class ONSCDesempenoEvaluationCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.competency'
    _description = u'Evaluación'
    _order = "name_skill,name"

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True)

    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo')
    improvement_areas = fields.Text(string='Brecha/Fortalezas/Aspectos a mejorar')
    name = fields.Text(string="Dimensión-Comportamiento esperado", readonly=True)
    name_skill = fields.Char(string="Nombre Competencia", related='skill_id.name', store=True)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"),
        ('bold', "Bold")],
        default='bold', help="Technical field for UX purpose.")
