# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import json

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
    _catalogs2validate = ['institution_id', 'subinstitution_id', 'institution_cert_id', 'subinstitution_cert_id']

    record_type = fields.Selection(TYPES, string='Tipo', required=True, default='course')
    course_type = fields.Selection(COURSE_TYPES, string='Tipo')
    course_title = fields.Char('Título del curso, taller u otra capacitación')
    certificate_id = fields.Many2one("onsc.cv.certificate", 'Título de la certificación')
    name = fields.Char(compute='_compute_name', store=True, string='Título')
    institution_cert_id = fields.Many2one('onsc.cv.certifying.institution', string=u'Institución certificadora')
    institution_cert_id_domain = fields.Char(compute='_compute_institution_cert_id_domain')
    subinstitution_cert_id = fields.Many2one('onsc.cv.certifying.subinstitution',
                                             string=u'Sub institución certificadora')
    dictation_mode = fields.Selection(MODES, 'Modalidad de dictado', required=True)
    induction_type = fields.Selection(INDUCTION_TYPES, 'Programa de inducción al Organismo', default="yes")
    hours_total = fields.Float('Carga horaria total (en horas)')
    approbation_mode = fields.Selection(APPROBATION_MODES, string='Modalidad de aprobación')
    evaluation_str = fields.Char('Nota obtenida')
    is_numeric_evaluation = fields.Boolean(compute='_compute_is_numeric_evaluation')
    evaluation_number = fields.Integer("Representación numérica de nota obtenida")
    evaluation_max_str = fields.Char("Nota máxima posible")
    evaluation_max_number = fields.Integer("Representación numérica de nota máxima posible")
    is_numeric_max_evaluation = fields.Boolean(compute='_compute_is_numeric_max_evaluation')
    line_ids = fields.One2many('onsc.cv.education.area.course', inverse_name='course_id',
                               string="Áreas relacionadas con esta educación")
    digital_doc_file = fields.Binary('Certificado/constancia', required=False)
    digital_doc_name = fields.Char('Nombre del documento digital')
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_acquired_course_rel',
                                              string=u'Conocimientos adquiridos', required=True,
                                              store=True)
    certificate_strat_date = fields.Date('Fecha de obtención del certificado / constancia',
                                         related='start_date', readonly=False)

    @api.depends('course_title', 'certificate_id', 'record_type')
    def _compute_name(self):
        for rec in self:
            rec.name = self._calc_name_by_record_type()

    @api.depends('evaluation_max_str')
    def _compute_is_numeric_max_evaluation(self):
        for rec in self:
            rec.is_numeric_max_evaluation = rec.evaluation_max_str and rec.evaluation_max_str.isnumeric() or False

    @api.depends('evaluation_str')
    def _compute_is_numeric_evaluation(self):
        for rec in self:
            rec.is_numeric_evaluation = rec.evaluation_str and rec.evaluation_str.isnumeric() or False

    @api.depends('certificate_id')
    def _compute_institution_cert_id_domain(self):
        for rec in self:
            valid_institution_cert_id_ids = rec.certificate_id.line_ids.mapped('institution_cert_id')
            rec.institution_cert_id_domain = json.dumps(
                [('id', 'in', valid_institution_cert_id_ids.ids)]
            )

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

    @api.onchange('course_title', 'certificate_id', 'record_type')
    def onchange_calc_name(self):
        self.name = self._calc_name_by_record_type()

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


class ONSCCVEducationAreaCourse(models.Model):
    _name = 'onsc.cv.education.area.course'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Áreas relacionadas con esta educación (cursos y certificados)'

    course_id = fields.Many2one('onsc.cv.course.certificate', 'Curso/Certificado')
