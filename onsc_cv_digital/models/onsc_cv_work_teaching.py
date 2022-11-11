# -*- coding: utf-8 -*-
from odoo import fields, models, api

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
    program_name = fields.Char('Nombre de la cátedra o programa académico')
    # Grilla Materias
    subject_ids = fields.One2many('onsc.cv.academic.program.subject', 'work_teaching_id', string='Materias', copy=True)
    # Grilla Áreas relacionadas con esta educación
    education_area_ids = fields.One2many('onsc.cv.education.area.teaching', inverse_name='teaching_id',
                                         string="Áreas relacionadas con esta educación", copy=True)
    other_relevant_information = fields.Text(string="Otra información relevante")

    # Grila Comprobantes
    receipt_ids = fields.One2many('onsc.cv.work.teaching.receipt.file', inverse_name='teaching_id',
                                  string='Comprobantes', copy=True)

    @api.onchange('subinstitution_id')
    def onchange_academic_program_id_parents(self):
        self.subject_ids = [(5,)]

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
    _inherit = ['onsc.cv.abstract.conditional.state', 'onsc.cv.abstract.formation']
    _catalogs_2validate = ['program_ids']

    cv_digital_id = fields.Many2one("onsc.cv.digital", required=False)
    work_teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade', required=True)
    program_ids = fields.Many2many('onsc.cv.academic.program', relation="academic_program_teaching_rel",
                                   string='Programas académicos', required=True, copy=True, ondelete='cascade')
    subject = fields.Char('Materia', required=True, )
    course_type = fields.Selection(COURSE_TYPES, 'Tipo de curso')
    currently_working_state = fields.Selection(string="¿Actualmente está enseñando la  materia?",
                                               selection=WORKING_STATE, required=True)
    level_teaching_type = fields.Selection(LEVEL_TEACHING_TYPES, 'Nivel enseñado de la materia', required=True)
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', string="Conocimientos enseñados",
                                              relation='knowledge_teaching_program_rel',
                                              required=True,
                                              copy=True,
                                              store=True)
    institution_id = fields.Many2one(related='work_teaching_id.institution_id')
    subinstitution_id = fields.Many2one(related='work_teaching_id.subinstitution_id')
    country_id = fields.Many2one(related='work_teaching_id.country_id')

    @api.model
    def create(self, values):
        _work_teaching_id = values.get('work_teaching_id')
        _subject = values.get('subject')
        _course_type = values.get('course_type')
        _level_teaching_type = values.get('level_teaching_type')
        _start_date = values.get('start_date')
        _end_date = values.get('end_date')
        all_values_tocheck = _work_teaching_id and _subject and _course_type and _level_teaching_type and _start_date and _end_date
        if all_values_tocheck and self.search_count([
            ('work_teaching_id', '=', _work_teaching_id),
            ('subject', '=', _subject),
            ('course_type', '=', _course_type)
            ('level_teaching_type', '=', _level_teaching_type)
            ('start_date', '=', _start_date)
            ('end_date', '=', _end_date)
        ]):
            return self
        return super(ONSCCVAcademicProgramSubject, self).create(values)

    def _get_json_dict(self):
        return [
            "id",
            "subject",
            "course_type",
            "currently_working_state",
            "level_teaching_type",
            ("program_ids", ['id',
                             'name',
                             ("study_level_id", ['id', 'name']),
                             ]),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
            ("country_id", ['id', 'name']),
        ]



class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.teaching'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (Docencia)'

    teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade')

    @api.model
    def create(self, values):
        _teaching_id = values.get('teaching_id')
        _educational_area_id = values.get('educational_area_id')
        _educational_subarea_id = values.get('educational_subarea_id')
        _discipline_educational_id = values.get('discipline_educational_id')
        all_values_tocheck = _teaching_id and _educational_area_id and _educational_subarea_id and _discipline_educational_id
        if all_values_tocheck and self.search_count([
            ('teaching_id', '=', _teaching_id),
            ('educational_area_id', '=', _educational_area_id),
            ('educational_subarea_id', '=', _educational_subarea_id),
            ('discipline_educational_id', '=', _discipline_educational_id),
        ]):
            return self
        return super(ONSCCVEducationAreaCourse, self).create(values)


class ONSCCVWorkInvestigationReceiptFile(models.Model):
    _name = 'onsc.cv.work.teaching.receipt.file'
    _description = 'Comprobantes de docencia'
    _inherit = 'onsc.cv.work.abstract.receipt.file'

    teaching_id = fields.Many2one('onsc.cv.work.teaching', 'Docencia', ondelete='cascade')

    @api.model
    def create(self, values):
        _teaching_id = values.get('teaching_id')
        _receipt_filename = values.get('receipt_filename')
        _receipt_description = values.get('receipt_description')
        all_values_tocheck = _teaching_id and _receipt_filename and _receipt_description
        if all_values_tocheck and self.search_count([
            ('teaching_id', '=', _teaching_id),
            ('receipt_filename', '=', _receipt_filename),
            ('receipt_description', '=', _receipt_description)
        ]):
            return self
        return super(ONSCCVEducationAreaCourse, self).create(values)
