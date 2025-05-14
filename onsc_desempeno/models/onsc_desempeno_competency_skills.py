# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoCompetencySkills(models.Model):
    _name = "onsc.desempeno.competency.skills"
    _description = "Información completa de formularios"

    token = fields.Char(string='Token', index=True)
    report_user_id = fields.Integer(string='Usuario que dió origen al reporte', index=True)
    consolidate_id = fields.Many2one('onsc.desempeno.consolidated', string='Competencia')
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia')
    dimension_id = fields.Many2one('onsc.desempeno.dimension', string="Dimensión")
    behavior = fields.Char(string="Comportamiento esperado")
    frequency_id = fields.Many2one(
        'onsc.desempeno.frequency.equivalence',
        string="Frecuencia del comportamiento esperado")
    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo')
    improvement_areas = fields.Text(string='Brecha/Fortalezas/Aspectos a mejorar')
