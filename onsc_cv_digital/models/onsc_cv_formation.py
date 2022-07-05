# -*- coding: utf-8 -*-

from odoo import fields, models, api

from . import onsc_cv_useful_tools as useful_tools
from .catalogs.onsc_cv_abstract_config import STATES as CATALOG_VALIDATION_STATES

STATES = [('incomplete', 'Incompleto'),
          ('in_progress', 'En curso'),
          ('completed', 'Finalizado')]

CATALOGS2VALIDATE = ['institution_id', 'subinstitution_id']


class ONSCCVFormationBasic(models.Model):
    _name = 'onsc.cv.basic.formation'
    _description = 'Formación básica'
    _order = 'start_date desc'

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV digital')
    basic_education_level = fields.Selection(string=u'Nivel de estudios básicos',
                                             selection=[('primary', u'Primaria'),
                                                        ('secondary', u'Secundaria'),
                                                        ('utu', u'UTU')], required=True)
    institution_id = fields.Many2one("onsc.cv.institution", string=u"Institución", required=True)
    subinstitution_id = fields.Many2one("onsc.cv.subinstitution", string=u"Sub institución", required=True)
    country_id = fields.Many2one('res.country', string=u'País de la institución', required=True)
    state = fields.Selection(string="Estado", selection=STATES, required=True)
    start_date = fields.Date(string="Fecha de inicio", required=True)
    end_date = fields.Date(string="Fecha finalización")
    coursed_years = fields.Text(string="Años cursados")
    other_relevant_information = fields.Text(string="Otra información relevante")
    study_certificate_file = fields.Binary(string="Certificado de estudio", required=True)
    study_certificate_name = fields.Char(string="Nombre certificado de estudio")

    # CATALOGS VALIDATION STATE
    conditional_validation_state = fields.Selection(
        string="Estado valor condicional",
        selection=CATALOG_VALIDATION_STATES,
        compute='_compute_conditional_validation_state',
        store=True
    )
    conditional_validation_reject_reason = fields.Char(
        compute='_compute_conditional_validation_state',
        store=True
    )

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id.id
            return {
                'domain': {
                    'country_id': [("id", "=", self.institution_id.country_id.id)]
                }
            }
        else:
            self.country_id = ''
            return {
                'domain': {
                    'country_id': []
                }
            }
        if (self.institution_id and self.institution_id != self.subinstitution_id.institution_id) or \
                self.institution_id is False:
            self.subinstitution_id = False

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id.id:
            return {
                'domain': {
                    'institution_id': [("country_id", "=", self.country_id.id), ("state", "=", 'validated')]
                }
            }
        else:
            return {
                'domain': {
                    'institution_id': [("state", "=", 'validated')]
                }
            }

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.end_date:
            if self.start_date and self.state == 'completed' and self.end_date <= self.start_date:
                self.end_date = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.start_date:
            if self.end_date and self.end_date <= self.start_date:
                self.end_date = self.start_date

    @api.depends('institution_id.state', 'subinstitution_id.state')
    def _compute_conditional_validation_state(self):
        for record in self:
            validation_status = useful_tools._get_validation_status(record, CATALOGS2VALIDATE)
            record.conditional_validation_state = validation_status.get('state')
            record.conditional_validation_reject_reason = validation_status.get('reject_reason', '')


class ONSCCVFormationAdvanced(models.Model):
    _name = 'onsc.cv.advanced.formation'
    _description = 'Formación avanzada'

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV digital')
    institution_id = fields.Many2one("onsc.cv.institution", string=u"Institución", required=True)
    subinstitution_id = fields.Many2one("onsc.cv.subinstitution", string=u"Sub institución", required=True)
    country_id = fields.Many2one('res.country', string=u'País de la institución', required=True)
    country_name = fields.Char(related="country_id.name")
    advanced_study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio avanzado', required=True)
    academic_program_id = fields.Many2one('onsc.cv.academic.program', string=u'Programa académico', required=True)
    homologated_title = fields.Selection(string=u'¿Su título esta revalidado/homologado en Uruguay?',
                                         selection=[('yes', u'Si'), ('no', u'No')])
    homologated_title_date = fields.Date(string="Fecha de revalidación",
                                         help='Fecha de revalidación/homologación de título')
    apostilled_title = fields.Selection(string=u'¿Su título esta apostillado?',
                                        selection=[('yes', u'Si'), ('no', u'No')])
    apostilled_date = fields.Date(string="Fecha de apostillado")
    state = fields.Selection(string="Estado", selection=STATES, required=True)
    start_date = fields.Date(string="Fecha de inicio", required=True)
    egress_date = fields.Date(string="Fecha de egreso")
    issue_title_date = fields.Date(string="Fecha de expedición Título")
    is_require_thesis = fields.Boolean(string="¿Su estudio requiere o requirió tesis?")
    state_thesis = fields.Selection(string=u'Estado de la tesis',
                                    selection=[('no_starting', u'Sin comenzar'), ('in_progress', u'En curso'),
                                               ('completed', u'Finalizado')])
    title_thesis = fields.Char(string="Título de la tesis")
    description_thesis = fields.Text(string="Describa su tesis")
    tutor = fields.Char(string="Tutor")
    knowledge_thesis_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_thesis_id',
                                            string=u'Conocimientos aplicados a su tesis',
                                            help='Sólo se pueden seleccionar 5 tipos de conocimientos')
    final_note_thesis = fields.Float(string="Nota final de tesis")
    max_note_thesis = fields.Float(string="Nota máxima posible de tesis")
    scholarship = fields.Float(string="Escolaridad", required=True)
    max_scholarship = fields.Float(string="Escolaridad máxima posible")
    credits_far = fields.Float(string="Créditos / Materias aprobadas hasta el momento")
    credits_training = fields.Float(string="Créditos / Materias totales de la formación")
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_acquired',
                                              string=u'Conocimientos adquiridos', required=True,
                                              help='Sólo se pueden seleccionar 5 tipos de conocimientos')
    area_related_education_ids = fields.One2many('onsc.cv.area.related.education', 'advanced_formation_id',
                                                 string=u'Áreas relacionadas con esta educación')
    other_relevant_information = fields.Text(string="Otra información relevante")
    egress_certificate_file = fields.Binary(string="Certificado de egreso / título / escolaridad", required=True)
    egress_certificate_name = fields.Char(string="Nombre certificado de egreso")
    revalidated_certificate_file = fields.Binary(string="Certificado de reválida de título",
                                                 help="Certificado de reválida de título / Resolución de reválida de título / Titulo revalidado")
    revalidated_certificate_name = fields.Char(string="Nombre certificado de reválida de título")
    homologated_certificate_file = fields.Binary(string="Certificado de homologación")
    homologated_certificate_name = fields.Char(string="Nombre certificado de homologación")
    apostille_file = fields.Binary(string="Apostilla")
    apostille_name = fields.Char(string="Nombre apostilla")

    # CATALOGS VALIDATION STATE
    conditional_validation_state = fields.Selection(
        string="Estado valor condicional",
        selection=CATALOG_VALIDATION_STATES,
        compute='_compute_conditional_validation_state',
        store=True
    )
    conditional_validation_reject_reason = fields.Char(
        compute='_compute_conditional_validation_state',
        store=True
    )

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id.id
            return {
                'domain': {
                    'country_id': [("id", "=", self.institution_id.country_id.id)]
                }
            }
        else:
            self.country_id = ''
            return {
                'domain': {
                    'country_id': []
                }
            }
        if (self.institution_id and self.institution_id != self.subinstitution_id.institution_id) or \
                self.institution_id is False:
            self.subinstitution_id = False

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id.id:
            return {
                'domain': {
                    'institution_id': [("country_id", "=", self.country_id.id), ("state", "=", 'validated')]
                }
            }
        else:
            return {
                'domain': {
                    'institution_id': [("state", "=", 'validated')]
                }
            }

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.egress_date:
            if self.start_date and self.state == 'completed' and self.egress_date <= self.start_date:
                self.egress_date = self.start_date

    @api.onchange('egress_date')
    def onchange_end_date(self):
        if self.start_date:
            if self.egress_date and self.egress_date <= self.start_date:
                self.egress_date = self.start_date

    @api.onchange('state', 'is_require_thesis')
    def onchange_state_is_require_thesis(self):
        if self.state == 'completed' and self.is_require_thesis:
            self.state_thesis = 'completed'
        else:
            self.state_thesis = ''

    @api.depends('institution_id.state', 'subinstitution_id.state')
    def _compute_conditional_validation_state(self):
        for record in self:
            validation_status = useful_tools._get_validation_status(record, CATALOGS2VALIDATE)
            record.conditional_validation_state = validation_status.get('state')
            record.conditional_validation_reject_reason = validation_status.get('reject_reason', '')


class ONSCCVAreaRelatedEducation(models.Model):
    _name = 'onsc.cv.area.related.education'
    _description = 'Área relacionada con esta educación'

    advanced_formation_id = fields.Many2one('onsc.cv.advanced.formation', string=u'Formación avanzada')
    educational_areas_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área de educación', required=True)
    educational_subareas_id = fields.Many2one('onsc.cv.educational.subarea', string=u'Sub área de educación',
                                              required=True)
    discipline_educational_id = fields.Many2one('onsc.cv.discipline.educational', string=u'Disciplina de educación',
                                                required=True)
