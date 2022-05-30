# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVAcademicProgram(models.Model):
    _name = 'onsc.cv.academic.program'
    _description = 'Programa Académico'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del programa académico", required=True)
    country_id = fields.Many2one('res.country', string=u'País de la institución', ondelete='restrict', required=True)
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución')
    subinstitution_id = fields.Many2one('onsc.cv.subinstitution', string=u'Sub institución')
    study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de Estudio')
