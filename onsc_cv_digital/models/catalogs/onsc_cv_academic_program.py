# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ONSCCVAcademicProgram(models.Model):
    _name = 'onsc.cv.academic.program'
    _description = 'Programa académico'
    _inherit = ['onsc.cv.abstract.config', 'onsc.cv.abstract.institution']

    name = fields.Char("Nombre del programa académico", required=True)
    study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio', tracking=True, required=True)

    def _check_validate(self, args2validate, message=""):
        if self.institution_id.state != 'validated' or self.subinstitution_id.state != 'validated':
            raise ValidationError(_("La Institución o la Sub institución no ha sido validada"))
        args2validate = [
            ('name', '=', self.name),
            ('subinstitution_id', '=', self.subinstitution_id.id),
        ]
        return super(ONSCCVAcademicProgram, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s, Subinstitución %s" % (
                self.name, self.subinstitution_id.display_name))
        )
