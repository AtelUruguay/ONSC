# -*- coding: utf-8 -*-

import json

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

from odoo import fields, models, api, _

TYPES = [('course', 'Curso'), ('certificate', 'Certificado')]
MODES = [('face_to_face', 'Presencial'), ('virtual', 'Virtual'), ('hybrid', 'Híbrido')]
INDUCTION_TYPES = [('yes', 'Sí'), ('no', 'No')]
APPROBATION_MODES = [('by_assistance', 'Por asistencia'), ('by_evaluation', 'Por evaluación')]
COURSE_FIELDS = ['course_title', 'institution_id', 'subinstitution_id', 'country_id',
                 'induction_type', 'hours_total', 'end_date']
CERTIFICATE_FIELDS = ['institution_cert_id', 'subinstitution_cert_id']
COURSE_TYPES = [('course', 'Curso'), ('workshop', 'Taller'), ('other', 'Otra capacitación')]


class ONSCCVCourseCertificate(models.Model):
    _name = 'onsc.cv.course.certificate'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _description = 'Cursos y certificados'
    _order = 'start_date desc'
    _catalogs_2validate = ['institution_id', 'subinstitution_id', 'institution_cert_id', 'subinstitution_cert_id']

    record_type = fields.Selection(TYPES, string='Tipo', required=True, default='course')
    course_type = fields.Selection(COURSE_TYPES, string='Tipo')
    course_title = fields.Text('Título del curso, taller u otra capacitación')
    name = fields.Char(compute='_compute_name', store=True, string='Título')
    institution_cert_id = fields.Many2one('onsc.cv.certifying.institution', string=u'Institución certificadora')
    subinstitution_cert_id = fields.Many2one('onsc.cv.certifying.subinstitution',
                                             string=u'Sub institución certificadora')
    certificate_id = fields.Many2one("onsc.cv.certificate", 'Título de la certificación')
    certificate_id_domain = fields.Char(compute='_compute_certificate_id_domain')
    dictation_mode = fields.Selection(MODES, 'Modalidad de dictado')
    induction_type = fields.Selection(INDUCTION_TYPES, 'Programa de inducción al Organismo', default="yes")
    hours_total = fields.Integer('Carga horaria total (en horas)')
    approbation_mode = fields.Selection(APPROBATION_MODES, string='Modalidad de aprobación')
    evaluation_str = fields.Char('Nota obtenida')
    is_numeric_evaluation = fields.Boolean(compute='_compute_is_numeric_evaluation')
    evaluation_number = fields.Integer("Representación numérica de nota obtenida")
    evaluation_max_str = fields.Char("Nota máxima posible")
    evaluation_max_number = fields.Integer("Representación numérica de nota máxima posible")
    is_numeric_max_evaluation = fields.Boolean(compute='_compute_is_numeric_max_evaluation')
    line_ids = fields.One2many('onsc.cv.education.area.course', inverse_name='course_id',
                               copy=True,
                               string="Áreas relacionadas con esta educación")
    digital_doc_file = fields.Binary('Certificado/constancia')
    digital_doc_filename = fields.Char('Nombre del documento digital')
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_acquired_course_rel',
                                              string=u'Conocimientos adquiridos',
                                              required=True,
                                              copy=True,
                                              ondelete='restrict',
                                              store=True)
    certificate_start_date = fields.Date('Fecha de obtención del certificado / constancia',
                                         related='start_date', readonly=False)
    institution_id_domain = fields.Char(compute='_compute_institution_id_domain')
    internal_course = fields.Selection(
        INDUCTION_TYPES,
        '¿Fue dictado/a internamente por un miembro de su empresa/organismo/institución en el que trabaja o trabajó?'
    )
    internal_course_name = fields.Char("Nombre de la empresa/organismo/institución")

    @api.onchange('certificate_start_date')
    def onchange_certificate_start_date(self):
        if self.certificate_start_date and self.certificate_start_date > fields.Date.today():
            self.start_date = False
            return cv_warning(_(u"La fecha de inicio debe ser menor que la fecha actual"))

    @api.depends('course_title', 'certificate_id', 'record_type')
    def _compute_name(self):
        for rec in self:
            rec.name = rec._calc_name_by_record_type()

    @api.depends('evaluation_max_str')
    def _compute_is_numeric_max_evaluation(self):
        for rec in self:
            rec.is_numeric_max_evaluation = rec.evaluation_max_str and rec.evaluation_max_str.isnumeric() or False

    @api.depends('evaluation_str')
    def _compute_is_numeric_evaluation(self):
        for rec in self:
            rec.is_numeric_evaluation = rec.evaluation_str and rec.evaluation_str.isnumeric() or False

    @api.depends('subinstitution_cert_id')
    def _compute_certificate_id_domain(self):
        for rec in self:
            valid_recordsets = rec.subinstitution_cert_id.certificate_line_ids.mapped('certificate_id')
            rec.certificate_id_domain = json.dumps(
                [('id', 'in', valid_recordsets.ids)]
            )

    @api.depends('country_id')
    def _compute_institution_id_domain(self):
        for rec in self:
            if rec.country_id:
                rec.institution_id_domain = json.dumps(
                    [('country_id', '=', rec.country_id.id), ('is_unformal_education', '=', True)]
                )
            else:
                rec.institution_id_domain = json.dumps(
                    [('is_unformal_education', '=', True)])

    @api.onchange('record_type')
    def onchange_record_type(self):
        if self.record_type == 'certificate':
            self.approbation_mode = 'by_evaluation'
            self.state = 'completed'
        self._clear_fields()

    @api.onchange('evaluation_str')
    def onchange_evaluation_str(self):
        if self.evaluation_str and self.evaluation_str.isnumeric():
            self.evaluation_number = int(self.evaluation_str)
        else:
            self.evaluation_number = 0
            self.evaluation_max_str = False

    @api.onchange('evaluation_max_str')
    def onchange_evaluation_max_str(self):
        if self.evaluation_max_str and self.evaluation_max_str.isnumeric():
            self.evaluation_max_number = int(self.evaluation_max_str)
        else:
            self.evaluation_max_number = 0

    @api.onchange('evaluation_number')
    def onchange_evaluation_number(self):
        result = self.check_evaluation('evaluation_number')
        if result:
            self.evaluation_number = 0
            return result

    @api.onchange('evaluation_max_number')
    def onchange_evaluation(self):
        result = self.check_evaluation('evaluation_max_number')
        if result:
            self.evaluation_max_number = self.evaluation_number
            return result

    @api.onchange('institution_cert_id')
    def onchange_institution_cert_id(self):
        if (self.institution_cert_id and self.institution_cert_id != self.subinstitution_cert_id.institution_cert_id) \
                or self.institution_cert_id.id is False:
            self.subinstitution_cert_id = False

    @api.onchange('subinstitution_cert_id')
    def onchange_subinstitution_cert_id(self):
        certificate_subinstitution_cert_ids = self.certificate_id.mapped('line_ids.subinstitution_cert_id').ids
        if (self.subinstitution_cert_id and self.subinstitution_cert_id not in certificate_subinstitution_cert_ids) \
                or self.subinstitution_cert_id.id is False:
            self.certificate_id = False

    @api.onchange('course_title', 'certificate_id', 'record_type')
    def onchange_calc_name(self):
        self.name = self._calc_name_by_record_type()

    @api.onchange('internal_course', 'country_id')
    def onchange_internal_course(self):
        Institution = self.env['onsc.cv.institution'].suspend_security()
        Subinstitution = self.env['onsc.cv.subinstitution'].suspend_security()

        if self.internal_course == 'yes':
            self.institution_id = Institution.search(
                [('is_default', '=', True), ('country_id', '=', self.country_id.id)]).id
            self.subinstitution_id = Subinstitution.search(
                [('institution_id', '=', self.institution_id.id), ('is_default', '=', True)]).id
        else:
            self.internal_course_name = False
            self.institution_id = False
            self.subinstitution_id = False

            # Auxiliary functions

    def _clear_fields(self):
        self.ensure_one()
        fields_list = []
        if self.record_type == 'course':
            fields_list = COURSE_FIELDS
        elif self.record_type == 'certificate':
            fields_list = CERTIFICATE_FIELDS
        for field in fields_list:
            setattr(self, field, False)

    def _calc_name_by_record_type(self):
        self.ensure_one()
        if self.record_type == 'course':
            return self.course_title
        elif self.certificate_id:
            return self.certificate_id.name
        return ''

    def check_evaluation(self, changed_field):
        """
        Utilizada para mostrar mensajes de advertencia en onchange de evaluación
        :return:
        """
        result = {
            'warning': {
                'title': _("Atención"),
                'type': 'notification',
            }
        }
        msg = ''
        if self.evaluation_max_number and self.evaluation_number and \
                self.evaluation_number > self.evaluation_max_number:
            if changed_field == 'evaluation_number':
                msg = _('La representación numérica de nota obtenida debe ser menor que '
                        'la representación numérica de nota máxima posible.')
            else:
                msg = _('La representación numérica de nota máxima posible debe ser mayor que la '
                        'representación numérica de nota obtenida.')

        elif self.evaluation_number < 0:
            msg = _("La representación numérica de nota obtenida debe ser mayor que 0")

        elif self.evaluation_max_number < 0:
            msg = _("La representación numérica de nota máxima posible debe ser mayor que 0")

        if msg:
            result['warning'].update({'message': msg})
        else:
            result = {}
        return result

    def _get_json_dict(self):
        json_dict = super(ONSCCVCourseCertificate, self)._get_json_dict()
        json_dict.extend([
            "record_type",
            "course_type",
            "course_title",
            "name",
            "dictation_mode",
            "induction_type",
            "hours_total",
            "approbation_mode",
            "evaluation_str",
            "evaluation_number",
            "evaluation_max_str",
            "evaluation_max_number",
            "max_scholarship",
            "certificate_start_date",
            "start_date",
            "end_date",
            "other_relevant_information",
            "state",
            "conditional_validation_state",
            "conditional_validation_reject_reason",
            ("country_id", ['id', 'name']),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
            ("institution_cert_id", ['id', 'name']),
            ("subinstitution_cert_id", ['id', 'name']),
            ("certificate_id", ['id', 'name']),
            ("line_ids", self.env['onsc.cv.education.area.course']._get_json_dict()),
            ("knowledge_acquired_ids", ['id', 'name']),
            "internal_course_name",
        ])
        return json_dict


class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.course'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (cursos y certificados)'
    _no_create_ifautosave = True

    course_id = fields.Many2one('onsc.cv.course.certificate', 'Curso/Certificado')

    def _get_json_dict(self):
        return [
            ("educational_area_id", ['id', 'name']),
            ("educational_subarea_id", ['id', 'name']),
            ("discipline_educational_id", ['id', 'name']),
        ]
