# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning


class ONSCCVFormationBasic(models.Model):
    _name = 'onsc.cv.basic.formation'
    _description = 'Formación básica'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _order = 'start_date desc'
    _catalogs_2validate = ['institution_id', 'subinstitution_id']

    basic_education_level = fields.Selection(string=u'Nivel de estudios básicos',
                                             selection=[('primary', u'Primaria'),
                                                        ('secondary', u'Secundaria'),
                                                        ('utu', u'UTU')], required=True)
    coursed_years = fields.Text(string="Años cursados")
    study_certificate_file = fields.Binary(string="Certificado de estudio", required=True)
    study_certificate_filename = fields.Char('Nombre del documento digital')


class ONSCCVFormationAdvanced(models.Model):
    _name = 'onsc.cv.advanced.formation'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _description = 'Formación avanzada'
    _catalogs_2validate = ['institution_id', 'subinstitution_id']

    advanced_study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio avanzado', required=True)
    academic_program_id = fields.Many2one('onsc.cv.academic.program', string=u'Programa académico', required=True)
    homologated_title = fields.Selection(string=u'¿Su título esta revalidado/homologado en Uruguay?',
                                         selection=[('yes', u'Si'), ('no', u'No')])
    homologated_title_date = fields.Date(string="Fecha de revalidación",)
    apostilled_title = fields.Selection(string=u'¿Su título esta apostillado?',
                                        selection=[('yes', u'Si'), ('no', u'No')])
    apostilled_date = fields.Date(string="Fecha de apostillado")
    egress_date = fields.Date(string="Fecha de egreso")
    issue_title_date = fields.Date(string="Fecha de expedición título")
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
    area_related_education_ids = fields.One2many('onsc.cv.area.related.education', 'advanced_formation_id',
                                                 string=u'Áreas relacionadas con esta educación')
    other_relevant_information = fields.Text(string="Otra información relevante")
    egress_certificate_file = fields.Binary(string="Certificado de egreso / título / escolaridad", required=True)
    egress_certificate_filename = fields.Char('Nombre del documento digital')
    revalidated_certificate_file = fields.Binary(string="Certificado de reválida de título",
                                                 help="Certificado de reválida de título / Resolución de reválida de título / Titulo revalidado")
    revalidated_certificate_filename = fields.Char('Nombre del documento digital')
    homologated_certificate_file = fields.Binary(string="Certificado de homologación")
    homologated_certificate_filename = fields.Char('Nombre del documento digital')
    apostille_file = fields.Binary(string="Apostilla")
    apostille_filename = fields.Char('Nombre del documento digital')

    country_code = fields.Char(related="country_id.code")

    @api.onchange('homologated_title_date')
    def onchange_homologated_title_date(self):
        if self.homologated_title_date and self.homologated_title_date > fields.Date.today():
            self.homologated_title_date = False
            return cv_warning(_(u"La fecha de revalidación debe ser menor que la fecha actual"))
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            self.start_date = False
            return cv_warning(_("El período desde no puede ser mayor que el período hasta"))

    @api.onchange('apostilled_date')
    def onchange_apostilled_date(self):
        if self.apostilled_date and self.apostilled_date > fields.Date.today():
            self.apostilled_date = False
            return cv_warning(_(u"La fecha de apostillado debe ser menor que la fecha actual"))
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            self.start_date = False
            return cv_warning(_("El período desde no puede ser mayor que el período hasta"))

    @api.onchange('egress_date')
    def onchange_egress_date(self):
        if self.egress_date and self.egress_date > fields.Date.today():
            self.egress_date = False
            return cv_warning(_(u"La fecha de egreso debe ser menor que la fecha actual"))
        if self.start_date and self.egress_date and self.egress_date <= self.start_date:
            self.egress_date = False
            return cv_warning(_("La fecha de egreso no puede ser menor que la fecha de inicio"))
        if self.issue_title_date and self.egress_date and self.issue_title_date < self.egress_date:
            self.egress_date = False
            return cv_warning(_(u"La fecha de egreso debe ser menor que la fecha de expedición"))

    @api.onchange('issue_title_date')
    def onchange_issue_title_date(self):
        if self.issue_title_date and self.issue_title_date > fields.Date.today():
            self.issue_title_date = False
            return cv_warning(_(u"La fecha de expedición debe ser menor que la fecha actual"))
        if self.issue_title_date and self.egress_date and self.issue_title_date < self.egress_date:
            self.issue_title_date = False
            return cv_warning(_(u"La fecha de expedición debe ser mayor o igual que la fecha de egreso"))

    @api.onchange('state', 'is_require_thesis')
    def onchange_state_is_require_thesis(self):
        if self.state == 'completed' and self.is_require_thesis:
            self.state_thesis = 'completed'
        else:
            self.state_thesis = ''

    @api.onchange('advanced_study_level_id', 'subinstitution_id')
    def onchange_academic_program_id_parents(self):
        program = self.academic_program_id
        cond1 = self.advanced_study_level_id.id is False or (self.advanced_study_level_id != program.study_level_id)
        cond2 = self.subinstitution_id.id is False or (self.subinstitution_id != program.subinstitution_id)
        if cond1 or cond2:
            self.academic_program_id = False

    @api.onchange('knowledge_thesis_ids')
    def onchange_knowledge_thesis_ids(self):
        if len(self.knowledge_thesis_ids) > 5:
            self.knowledge_thesis_ids = self.knowledge_thesis_ids[:5]
            return cv_warning(_(u"Sólo se pueden seleccionar 5 tipos de conocimientos"))


class ONSCCVAreaRelatedEducation(models.Model):
    _name = 'onsc.cv.area.related.education'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Área relacionada con esta educación'

    advanced_formation_id = fields.Many2one('onsc.cv.advanced.formation',
                                            string=u'Formación avanzada',
                                            ondelete='cascade')
