# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning

POSITION_TYPES = [('effective', 'Efectivo'), ('interim', 'Interino'), ('honorary', 'Honorario')]
RESPONSIBLE_TYPES = [('yes', 'Sí'), ('no', 'No')]

COURSE_TYPES = [('theorist', 'Teórico'), ('practical', 'Práctico'), ('both', 'Teórico-práctico')]
WORKING_STATE = [('yes', 'Sí'), ('no', 'No')]
LEVEL_TEACHING_TYPES = [('primary', 'Primaria'), ('secondary', 'Secundaria'),
                        ('technical', 'Técnico'), ('tertiary', 'Grado terciario'),
                        ('postgraduate', 'Postgrado'), ('master', 'Maestría'),
                        ('doctorate', 'Doctorado'), ('postdoc', 'Postdoctorado')]


class ONSCCVWorkTeaching(models.Model):
    _name = 'onsc.cv.work.teaching'
    _description = 'Docencia'
    _inherit = ['onsc.cv.abstract.work', 'onsc.cv.abstract.conditional.state', 'onsc.cv.abstract.institution']
    _catalogs2validate = ['institution_id', 'subinstitution_id', 'professional_link_id']

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade', required=True)
    professional_link_id = fields.Many2one('onsc.cv.professional.link', 'Vínculo profesional', required=True)
    position_type = fields.Selection(POSITION_TYPES, 'Tipo de cargo')
    is_full_time = fields.Boolean('¿Dedicación total?')
    responsible_type = fields.Selection(RESPONSIBLE_TYPES, '¿Es responsable de cátedra o de programa académico?',
                                        required=True)
    program_name = fields.Char('Nombre de la cátedra o programa académico')
    # Grilla Materias
    subject_ids = fields.One2many('onsc.cv.academic.program.subject', 'work_teaching_id', string='Materias')
    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.cv.education.area.teaching', inverse_name='teaching_id',
                                         string="Áreas relacionadas con esta educación")
    other_relevant_information = fields.Text(string="Otra información relevante")
    receipt_description = fields.Char('Descripción del comprobante')

    @api.onchange('subinstitution_id')
    def onchange_academic_program_id_parents(self):
        self.subject_ids = [(5,)]


class ONSCCVAcademicProgramSubject(models.Model):
    _name = 'onsc.cv.academic.program.subject'
    _description = 'Materias'
    _inherit = 'onsc.cv.abstract.conditional.state'
    _catalogs2validate = ['program_ids']

    work_teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade', required=True)
    program_ids = fields.Many2many('onsc.cv.academic.program', relation="academic_program_teaching_rel",
                                   string='Programas académicos', required=True, ondelete='cascade')
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
    institution_id = fields.Many2one(related='work_teaching_id.institution_id')
    subinstitution_id = fields.Many2one(related='work_teaching_id.subinstitution_id')
    country_id = fields.Many2one(related='work_teaching_id.country_id')

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            self.start_date = False
            return cv_warning(_("El período desde no puede ser mayor que el período hasta"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            self.end_date = False
            return cv_warning(_("El período hasta no puede ser menor que el período desde"))

    @api.onchange('knowledge_teaching_ids')
    def onchange_knowledge_teaching_ids(self):
        if len(self.knowledge_teaching_ids) > 5:
            self.knowledge_teaching_ids = self.knowledge_acquired_ids[:5]
            return cv_warning(_("Sólo se pueden seleccionar 5 tipos de conocimientos"))


class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.teaching'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (Docencia)'

    teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia')
