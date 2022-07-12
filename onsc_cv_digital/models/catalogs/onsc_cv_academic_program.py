# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

COURSE_TYPES = [('theorist', 'Teórico'), ('practical', 'Práctico'), ('both', 'Teórico-práctico')]
WORKING_STATE = [('yes', 'Sí'), ('no', 'No')]
LEVEL_TEACHING_TYPES = [('primary', 'Primaria'), ('secondary', 'Secundaria'),
                        ('technical', 'Técnico'), ('tertiary', 'Grado terciario'),
                        ('postgraduate', 'Postgrado'), ('master', 'Maestría'),
                        ('doctorate', 'Doctorado'), ('postdoc', 'Postdoctorado')]


class ONSCCVAcademicProgram(models.Model):
    _name = 'onsc.cv.academic.program'
    _description = 'Programa académico'
    _inherit = ['onsc.cv.abstract.config', 'onsc.cv.abstract.institution']

    name = fields.Char("Nombre del programa académico", required=True)
    study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio', tracking=True, required=True)
    subject_ids = fields.One2many('onsc.cv.academic.program.subject', 'program_id', string='Materias')

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


class ONSCCVAcademicProgramSubject(models.Model):
    _name = 'onsc.cv.academic.program.subject'
    _description = 'Materias del programa académico'

    program_id = fields.Many2one('onsc.cv.academic.program', 'Programa académico', required=True, ondelete='cascade')
    subject = fields.Char('Materia')
    course_type = fields.Selection(COURSE_TYPES, 'Tipo de curso')
    currently_working_state = fields.Selection(string="¿Actualmente está enseñando la  materia?",
                                               selection=WORKING_STATE, required=True)
    start_date = fields.Date("Período desde dando esta materia", required=True)
    end_date = fields.Date("Período hasta dando esta materia")
    level_teaching_type = fields.Selection(LEVEL_TEACHING_TYPES, 'Nivel enseñado de la materia', required=True)
    knowledge_teaching_ids = fields.Many2many('onsc.cv.knowledge', string="Conocimientos enseñados",
                                              relation='knowledge_teaching_program_rel', required=True,
                                              help="Sólo se pueden seleccionar 5")

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.state == 'completed' and self.end_date <= self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            self.end_date = self.start_date

    @api.onchange('knowledge_teaching_ids')
    def onchange_knowledge_teaching_ids(self):
        if len(self.knowledge_teaching_ids) > 5:
            self.knowledge_teaching_ids = self.knowledge_acquired_ids[:5]
            return {
                'warning': {
                    'title': _("Atención"),
                    'type': 'notification',
                    'message': _(
                        "Sólo se pueden seleccionar 5 tipos de conocimientos"
                    )
                },

            }
