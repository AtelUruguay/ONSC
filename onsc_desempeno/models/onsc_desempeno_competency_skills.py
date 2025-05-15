# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCDesempenoCompetencySkills(models.Model):
    _name = "onsc.desempeno.competency.skills"
    _description = "Información completa de formularios"
    _order = "skill_id"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCDesempenoCompetencySkills, self).fields_get(allfields, attributes)
        hide = [
            'consolidate_id',
            'report_user_id',
            'token',
            'create_uid',
            'write_uid',
            'create_date',
            'write_date',

        ]
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

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
