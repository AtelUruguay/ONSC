# -*- coding: utf-8 -*-
from odoo import fields, models

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
    _catalogs_2validate = ['institution_id', 'subinstitution_id', 'professional_link_id']
    _order = 'start_date desc'

    professional_link_id = fields.Many2one('onsc.cv.professional.link', 'Vínculo profesional', required=True)
    position_type = fields.Selection(POSITION_TYPES, 'Tipo de cargo')
    is_full_time = fields.Boolean('¿Dedicación total?')
    responsible_type = fields.Selection(RESPONSIBLE_TYPES, '¿Es responsable de cátedra o de programa académico?',
                                        required=True)
    # Grilla Materias
    subject_ids = fields.One2many('onsc.cv.academic.program.subject', 'work_teaching_id', string='Materias', copy=True)
    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.cv.education.area.teaching', inverse_name='teaching_id',
                                         string="Áreas relacionadas con esta educación", copy=True)
    other_relevant_information = fields.Text(string="Otra información relevante")

    # Grila Comprobantes
    receipt_ids = fields.One2many('onsc.cv.work.teaching.receipt.file', inverse_name='teaching_id',
                                  string='Comprobantes', copy=True)

    def _get_json_dict(self):
        json_dict = super(ONSCCVWorkTeaching, self)._get_json_dict()
        json_dict.extend([
            "hours_worked_monthly",
            "currently_working",
            "position",
            "is_paid_activity",
            "country_id",
            "company_type",
            "company_name",
            "description_tasks",
            "start_date",
            "end_date",
            "position_type",
            "is_full_time",
            "responsible_type",
            "program_name",
            "other_relevant_information",
            "receipt_description",
            "conditional_validation_state",
            "conditional_validation_reject_reason",
            ("country_id", ['id', 'name']),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
            ("professional_link_id", ['id', 'name']),
            ("subject_ids", self.env['onsc.cv.academic.program.subject']._get_json_dict()),
            ("education_area_ids", self.env['onsc.cv.education.area.teaching']._get_json_dict()),
        ])
        return json_dict


class ONSCCVAcademicProgramSubject(models.Model):
    _name = 'onsc.cv.academic.program.subject'
    _description = 'Materias'
    _inherit = ['onsc.cv.abstract.formation']
    _no_create_ifautosave = True

    cv_digital_id = fields.Many2one("onsc.cv.digital", required=False)
    work_teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade', required=True)
    subject = fields.Char('Materia', required=True, )
    course_type = fields.Selection(COURSE_TYPES, 'Tipo de curso')
    currently_working_state = fields.Selection(string="¿Actualmente está enseñando la  materia?",
                                               selection=WORKING_STATE, required=True)
    level_teaching_type = fields.Selection(LEVEL_TEACHING_TYPES, 'Nivel enseñado de la materia', required=True)
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', string="Conocimientos enseñados",
                                              relation='knowledge_teaching_program_rel',
                                              required=True,
                                              copy=True,
                                              ondelete='restrict',
                                              store=True)

    def _get_json_dict(self):
        return [
            "id",
            "subject",
            "course_type",
            "currently_working_state",
            "level_teaching_type",
        ]


class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.teaching'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (Docencia)'
    _no_create_ifautosave = True

    teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade')


class ONSCCVWorkInvestigationReceiptFile(models.Model):
    _name = 'onsc.cv.work.teaching.receipt.file'
    _description = 'Comprobantes de docencia'
    _inherit = 'onsc.cv.work.abstract.receipt.file'
    _no_create_ifautosave = True

    teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade')
