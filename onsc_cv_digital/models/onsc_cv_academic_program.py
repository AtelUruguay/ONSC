# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVAcademicProgram(models.Model):
    _name = 'onsc.cv.academic.program'
    _description = 'Programa Académico'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del programa académico", required=True)
    country_id = fields.Many2one('res.country', string=u'País de la institución', ondelete='restrict', required=True)
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución', tracking=True, required=True)
    subinstitution_id = fields.Many2one('onsc.cv.subinstitution', string=u'Sub institución', tracking=True,
                                        required=True)
    study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de Estudio', tracking=True, required=True)

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id and self.country_id != self.institution_id.country_id:
            self.institution_id = False

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id
        if self.institution_id and self.institution_id != self.subinstitution_id.institution_id:
            self.subinstitution_id = False
