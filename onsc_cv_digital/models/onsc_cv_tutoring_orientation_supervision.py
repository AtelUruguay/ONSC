# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from .abstracts.onsc_cv_abstract_work import PAID_ACTIVITY_TYPES
from .onsc_cv_useful_tools import is_valid_url, is_exist_url
from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning

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
    tutor_type_id = fields.Many2one('onsc.cv.type.tutor', string='Tipo/clase', required=True)
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
    is_tutoring_finished = fields.Boolean('Tutoría conluida')
    year_title = fields.Selection(YEARS_TITLE, 'Año de obtención del título')
    orientation_type_id = fields.Many2one('onsc.cv.type.orientation', 'Tipo de orientación', required=True)
    co_tutor_name = fields.Char('Nombre del co-tutor')
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=PAID_ACTIVITY_TYPES)
    is_relevant_work = fields.Boolean('¿Es uno de los cinco trabajos más relevantes de su producción?')
    #  Grilla área de actividad
    area_ids = fields.One2many('onsc.cv.education.area.tutoring', 'tutoring_id', 'Área de actividad')
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', relation='knowledge_acquired_tutoring_rel',
                                              string='Conocimientos aplicados', store=True, required=True)
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

    @api.onchange('year_title')
    def onchange_year_title(self):
        if self.start_date and self.year_title and fields.Date.from_string(self.start_date).year > int(self.year_title):
            self.start_date = False
        if self.end_date and self.year_title and fields.Date.from_string(self.end_date).year != int(self.year_title):
            self.end_date = False

    @api.onchange('start_date')
    def onchange_start_date(self):
        res = super(ONSCCVTutorialOrientationSupervision, self).onchange_start_date()
        if res:
            return res
        if self.start_date and self.year_title:
            if fields.Date.from_string(self.start_date).year > int(self.year_title):
                self.start_date = False
                return cv_warning(
                    _("El año de la fecha de inicio debe ser menor o igual al año de obtención del título"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        res = super(ONSCCVTutorialOrientationSupervision, self).onchange_start_date()
        if res:
            return res
        if self.end_date and self.year_title:
            if fields.Date.from_string(self.end_date).year != int(self.year_title):
                self.end_date = False
                return cv_warning(
                    _("El año de la fecha de finalización debe ser igual al año de obtención del título"))

    @api.onchange('is_tutoring_finished')
    def onchange_is_tutoring_finished(self):
        self.year_title = False
        self.end_date = False

    @api.onchange('website')
    def onchange_website(self):
        if self.website and not is_valid_url(self.website):
            self.website = False
            return cv_warning(_("EL sitio web no tiene un formato válido."))
        elif self.website and not is_exist_url(self.website):
            self.website = False
            return cv_warning(_("El sitio web no existe"))


class ONSCCVEducationAreaTutorial(models.Model):
    _name = 'onsc.cv.education.area.tutoring'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (tutorías, orientaciones, supervisiones)'

    tutoring_id = fields.Many2one('onsc.cv.tutoring.orientation.supervision', 'Tutoría, Orientación, Supervisión',
                                  ondelete='cascade', required=True)
    speciality = fields.Char(string=u"Especialidad")
