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


class ONSCDesempenoEvaluationCompentency(models.Model):
    _name = 'onsc.desempeno.evaluation.compentency'
    _description = u'Evaluación'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True)
    dimension = fields.Text(string='Dimensiones', compute='_compute_dimension', store=True)
    expected_behavior = fields.Text(string='Comportamiento Esperado', readonly=True)
    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo', readonly=True,
                                states={'in_progress': [('readonly', False)]})
    improvement_areas = fields.Text(string='Brecha / Fortalezas / Aspectos a mejorar', readonly=True,
                                    states={'in_progress': [('readonly', False)]})

    @api.depends('skill_id')
    def _compute_dimension(self):
        SkillLine = self.env('onsc.desempeno.skill.line').suspend_security()
        for record in self:

            dimensions = SkillLine.search([('id', 'in', record.skill_id.ids)]).dimension_id

            html_list = '<ul>\n'
            for dimension in dimensions:
                html_list += f'<li>{dimension}</li>\n'
            html_list += '</ul>'

            text = html2text.html2text(html_list)
            record.description = text

        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()
