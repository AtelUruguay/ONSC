# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

from .abstracts.onsc_cv_abstract_work import PAID_ACTIVITY_TYPES
from .onsc_cv_useful_tools import is_valid_url, is_exist_url

POSTGRADUATE_TYPES = [('academic', 'Académico'), ('professional', 'Profesional')]
YEARS_TITLE = [('%s' % x, '%s' % x) for x in range(fields.Date.today().year, 1900, -1)]


class ONSCCVTutorialOrientationSupervision(models.Model):
    _name = 'onsc.cv.tutoring.orientation.supervision'
    _description = 'Tutorías, Orientaciones, Supervisiones'
    _inherit = ['onsc.cv.abstract.institution', 'onsc.cv.abstract.formation', 'onsc.cv.abstract.conditional.state']
    _catalogs_2validate = ['institution_id', 'subinstitution_id', 'academic_program_id']
    _order = 'start_date desc'

    work_title = fields.Char('Título del trabajo', required=True)
    tutor_type_id = fields.Many2one('onsc.cv.type.tutor', string='Tipo/clase', required=True)
    is_tutor_option_other_enable = fields.Boolean(related='tutor_type_id.is_option_other_enable')
    other_tutor_type = fields.Char('Otro tipo/clase')
    dependence = fields.Char('Dependencia')
    academic_program_id = fields.Many2one('onsc.cv.academic.program', string=u'Programa académico', required=True)
    postgraduate_type = fields.Selection(POSTGRADUATE_TYPES, 'Tipo posgrado')
    student_name = fields.Char('Nombre del orientado/estudiante', required=True)
    language_id = fields.Many2one('onsc.cv.language', 'Idioma', required=True)
    description = fields.Text('Descripción')
    divulgation_media_id = fields.Many2one('onsc.cv.divulgation.media', 'Medio de divulgación')
    is_tutor_docent = fields.Boolean(compute='_compute_tutor_type')
    is_tutor_master = fields.Boolean(compute='_compute_tutor_type')
    is_divulgation_option_other_enable = fields.Boolean(related='divulgation_media_id.is_option_other_enable')
    other_divulgation_media = fields.Char('Otro medio de divulgación')
    website = fields.Char('Sitio web')
    is_tutoring_finished = fields.Boolean('Tutoría conluida')
    orientation_type_id = fields.Many2one('onsc.cv.type.orientation', 'Tipo de orientación', required=True)
    co_tutor_name = fields.Char('Nombre del co-tutor')
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=PAID_ACTIVITY_TYPES, required=True)
    is_relevant_work = fields.Boolean('¿Es uno de los cinco trabajos más relevantes de su producción?')
    #  Grilla área de actividad
    area_ids = fields.One2many('onsc.cv.education.area.tutoring', 'tutoring_id', 'Área de actividad', copy=True)
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', relation='knowledge_acquired_tutoring_rel',
                                              string='Conocimientos aplicados', store=True, required=True, copy=True)
    is_orientation_type_pie = fields.Boolean(compute='_compute_is_orientation_type_pie')
    receipt_file = fields.Binary("Comprobante")
    receipt_filename = fields.Char('Nombre del documento digital')

    @api.depends('orientation_type_id')
    def _compute_is_orientation_type_pie(self):
        for rec in self:
            rec.is_orientation_type_pie = rec.orientation_type_id == self.env.ref(
                'onsc_cv_digital.onsc_cv_type_orientation_cotutor_pie')

    @api.depends('tutor_type_id')
    def _compute_tutor_type(self):
        for rec in self:
            rec.is_tutor_docent = rec.tutor_type_id == self.env.ref('onsc_cv_digital.onsc_cv_type_tutor_docent')
            rec.is_tutor_master = rec.tutor_type_id == self.env.ref('onsc_cv_digital.onsc_cv_type_tutor_master')

    @api.onchange('is_tutoring_finished')
    def onchange_is_tutoring_finished(self):
        self.end_date = False

    @api.onchange('website')
    def onchange_website(self):
        if self.website and not is_valid_url(self.website):
            self.website = False
            return cv_warning(_("El sitio web no tiene un formato válido."))
        elif self.website and not is_exist_url(self.website):
            self.website = False
            return cv_warning(_("El sitio web no existe"))

    @api.onchange('tutor_type_id')
    def onchange_tutor_type_id(self):
        self.other_tutor_type = False
        self.orientation_type_id = False

    @api.onchange('divulgation_media_id')
    def onchange_divulgation_media_id(self):
        self.other_divulgation_media = False

    def _get_json_dict(self):
        json_dict = super(ONSCCVTutorialOrientationSupervision, self)._get_json_dict()
        json_dict.extend([
            "work_title",
            "other_tutor_type",
            "dependence",
            "postgraduate_type",
            "student_name",
            "description",
            "website",
            "is_tutoring_finished",
            "co_tutor_name",
            "is_paid_activity",
            "is_relevant_work",
            "start_date",
            "end_date",
            "other_relevant_information",
            "other_divulgation_media",
            "conditional_validation_state",
            "conditional_validation_reject_reason",
            ("country_id", ['id', 'name']),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
            ("tutor_type_id", ['id', 'name']),
            ("academic_program_id", ['id', 'name']),
            ("language_id", ['id', 'name']),
            ("divulgation_media_id", ['id', 'name']),
            ("orientation_type_id", ['id', 'name']),
            ("area_ids", self.env['onsc.cv.education.area.tutoring']._get_json_dict()),
            ("knowledge_acquired_ids", ['id', 'name']),
            ("knowledge_acquired_ids", ['id', 'name'])
        ])
        return json_dict


class ONSCCVEducationAreaTutorial(models.Model):
    _name = 'onsc.cv.education.area.tutoring'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (tutorías, orientaciones, supervisiones)'

    tutoring_id = fields.Many2one('onsc.cv.tutoring.orientation.supervision', 'Tutoría, Orientación, Supervisión',
                                  ondelete='cascade', required=True)
    speciality = fields.Char(string=u"Especialidad", required=True)

    @api.model
    def create(self, values):
        _tutoring_id = values.get('tutoring_id')
        _educational_area_id = values.get('educational_area_id')
        _educational_subarea_id = values.get('educational_subarea_id')
        _discipline_educational_id = values.get('discipline_educational_id')
        all_values_tocheck = _tutoring_id and _educational_area_id and _educational_subarea_id and _discipline_educational_id
        if all_values_tocheck and self.search_count([
            ('tutoring_id', '=', _tutoring_id),
            ('educational_area_id', '=', _educational_area_id),
            ('educational_subarea_id', '=', _educational_subarea_id),
            ('discipline_educational_id', '=', _discipline_educational_id),
        ]):
            return self
        return super(ONSCCVEducationAreaTutorial, self).create(values)

    def _get_json_dict(self):
        json_dict = super(ONSCCVEducationAreaTutorial, self)._get_json_dict()
        json_dict.extend([
            "speciality"
        ])
        return json_dict
