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
    _order = "name_skill"

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True)
    skill_line_ids = fields.One2many(comodel_name="onsc.desempeno.skill.line", inverse_name="competency_id",
                                     string="Lineas de competencia",
                                     )

    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo', required=True)
    improvement_areas = fields.Text(string='Brecha/Fortalezas/Aspectos a mejorar', required=True, help='Este es un tooltip para el campo Brecha/Fortalezas/Aspectos a mejorar')
    name_skill = fields.Char(string="Nombre Competencia", related='skill_id.name')

    def button_open_current_skill(self):
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_competency_action').read()[0]
        action.update({'res_id': self.id})
        return action
