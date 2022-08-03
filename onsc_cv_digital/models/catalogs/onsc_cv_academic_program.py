# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ONSCCVAcademicProgram(models.Model):
    _name = 'onsc.cv.academic.program'
    _description = 'Programa académico'
    _inherit = ['onsc.cv.abstract.config', 'onsc.cv.abstract.institution']
    _fields_2check_unicity = ['name', 'subinstitution_id', 'state']

    name = fields.Char("Nombre del programa académico", required=True)
    study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio', tracking=True, required=True)

    def _check_validation_status(self):
        parent_states = self.mapped('subinstitution_id.state')
        if 'to_validate' in parent_states or 'rejected' in parent_states:
            raise ValidationError(_("No se puede un Programa académico si "
                                    "la Sub institución y la Institución no está validada"))
        return super(ONSCCVAcademicProgram, self)._check_validation_status()

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s, Subinstitución %s" % (self.name,
                                                                                self.subinstitution_id.display_name))

    def _check_parent_validation_state(self):
        if self.institution_id.state != 'validated' or self.subinstitution_id.state != 'validated':
            raise ValidationError(_("La Institución o la Sub institución no ha sido validada"))
