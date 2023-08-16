# -*- coding: utf-8 -*-
import logging

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
    _order = "name_skill,name_dimension"

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True)

    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo')
    improvement_areas = fields.Text(string='Brecha / Fortalezas / Aspectos a mejorar')
    skill_line_ids = fields.Many2many('onsc.desempeno.skill.line', 'skill_line_competency_rel', 'compentency_id',
                                      'skill_line_id',
                                      string='Entorno')
    dimension_id = fields.Many2one('onsc.desempeno.dimension', string="Dimensión", readonly=True)
    behavior = fields.Char(string="Comportamiento esperado", readonly=True)
    name_dimension = fields.Char(string="Nombre dimension", related='dimension_id.name', store=True)
    name_skill = fields.Char(string="Nombre Competencia", related='skill_id.name', store=True)

    @api.onchange('degree_id')
    def onchange_degree_id(self):
        self.search([('evaluation_id', '=', self.evaluation_id.id.origin), ('skill_id', '=', self.skill_id.id)]).suspend_security().write(
            {'degree_id': self.degree_id.id})
