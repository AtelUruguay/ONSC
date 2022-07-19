# -*- coding: utf-8 -*-

from odoo import fields, models, api
from .abstracts.onsc_cv_abstract_work import PAID_ACTIVITY_TYPES

POSTGRADUATE_TYPES = [('academic', 'Académico'), ('professional', 'Profesional')]
YEARS_TITLE = [('%s' % x, '%s' % x) for x in range(fields.Date.today().year, 1900, -1)]


class ONSCCVTutorialOrientationSupervision(models.Model):
    _name = 'onsc.cv.tutoring.orientation.supervision'
    _description = 'Tutorías, Orientaciones, Supervisiones'
    _inherit = ['onsc.cv.abstract.institution', 'onsc.cv.abstract.formation', 'onsc.cv.abstract.conditional.state']
    _catalogs2validate = ['institution_id', 'subinstitution_id', 'academic_program_id']
    _order = 'date desc'

    work_title = fields.Char('Título del trabajo', required=True)
    date = fields.Date('Fecha', required=True)
    tutor_type_id = fields.Many2one('onsc.cv.research.types.classes', string='Tipo/clase', required=True)
    is_tutor_option_other_enable = fields.Boolean(related='tutor_type_id.is_option_other_enable')
    other_tutor_type = fields.Char('Otro tipo/clase')
    dependence = fields.Char('Dependencia')
    academic_program_id = fields.Many2one('onsc.cv.academic.program', string=u'Programa académico', required=True)
    postgraduate_type = fields.Selection(POSTGRADUATE_TYPES, 'Tipo posgrado', required=True)
    student_name = fields.Char('Nombre del orientado/estudiante', required=True)
    language_id = fields.Many2one('onsc.cv.language', 'Idioma', required=True)
    description = fields.Text('Descripción')
    divulgation_media_id = fields.Many2one('onsc.cv.divulgation.media', 'Medio de divulgación')
    is_tutor_docent = fields.Boolean(compute='_compute_is_tutor_docent')
    is_divulgation_option_other_enable = fields.Boolean(related='divulgation_media_id.is_option_other_enable')
    other_divulgation_media = fields.Char('Otro medio de divulgación')
    website = fields.Char('Sitio web')
    is_tutoring_included = fields.Boolean('Tutoría incluida')
    year_title = fields.Selection(YEARS_TITLE, 'Año de obtención del título')
    orientation_type_id = fields.Many2one('onsc.cv.type.orientation', 'Tipo de orientación', required=True)
    co_tutor_name = fields.Char('Nombre del co-tutor')
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=PAID_ACTIVITY_TYPES)
    is_relevant_work = fields.Boolean('¿Es uno de los cinco trabajos más relevantes de su producción?')
    #  Grilla área de actividad
    area_ids = fields.One2many('onsc.cv.education.area.tutoring', 'tutoring_id', 'Área de actividad')
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', relation='knowledge_acquired_tutoring_rel',
                                              string='Conocimientos aplicados', store=True)
    is_orientation_type_pie = fields.Boolean(compute='_compute_is_orientation_type_pie')

    @api.depends('orientation_type_id')
    def _compute_is_orientation_type_pie(self):
        for rec in self:
            rec.is_orientation_type_pie = rec.orientation_type_id == self.env.ref(
                'onsc_cv_digital.onsc_cv_type_orientation_cotutor_pie')

    @api.depends('tutor_type_id')
    def _compute_is_tutor_docent(self):
        for rec in self:
            rec.is_tutor_docent = rec.tutor_type_id == self.env.ref('onsc_cv_digital.onsc_cv_type_tutor_docent')


class ONSCCVEducationAreaTutorial(models.Model):
    _name = 'onsc.cv.education.area.tutoring'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (tutorías, orientaciones, supervisiones)'

    tutoring_id = fields.Many2one('onsc.cv.tutoring.orientation.supervision', 'Tutoría, Orientación, Supervisión',
                                  ondelete='cascade', required=True)
    speciality = fields.Char(string=u"Especialidad")
