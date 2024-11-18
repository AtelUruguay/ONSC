# -*- coding: utf-8 -*-

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

from odoo import fields, models, api, _


class ONSCCVFormationBasic(models.Model):
    _name = 'onsc.cv.basic.formation'
    _description = 'Formación básica'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _order = 'start_date desc'
    _catalogs_2validate = ['institution_id', 'subinstitution_id']

    basic_education_level = fields.Selection(string=u'Nivel de estudios básicos',
                                             selection=[('primary', u'Primaria'),
                                                        ('secondary', u'Secundaria')], required=True)
    coursed_years = fields.Text(string="Años cursados")
    study_certificate_file = fields.Binary(string="Certificado de estudio")
    study_certificate_filename = fields.Char('Nombre del documento digital - Certificado de estudio')

    @api.onchange('state')
    def onchange_state(self):
        self.end_date = False

    @api.model
    def create(self, values):
        result = super(ONSCCVFormationBasic, self).create(values)
        return result

    def _get_json_dict(self):
        json_dict = super(ONSCCVFormationBasic, self)._get_json_dict()
        json_dict.extend([
            "start_date",
            "end_date",
            "basic_education_level",
            "coursed_years",
            "other_relevant_information",
            "state",
            "conditional_validation_state",
            "conditional_validation_reject_reason",
            ("country_id", ['id', 'name']),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
        ])
        return json_dict


class ONSCCVFormationAdvanced(models.Model):
    _name = 'onsc.cv.advanced.formation'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _description = 'Formación avanzada'
    _catalogs_2validate = ['institution_id', 'subinstitution_id']
    _order = 'start_date desc'

    advanced_study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio avanzado', required=True)
    academic_program_id = fields.Many2one('onsc.cv.academic.program', string=u'Programa académico')
    homologated_title = fields.Selection(string=u'¿Su título está revalidado/homologado en Uruguay?',
                                         selection=[('yes', u'Si'), ('no', u'No')])
    homologated_title_date = fields.Date(string="Fecha de revalidación", )
    apostilled_title = fields.Selection(string=u'¿Su título está apostillado?',
                                        selection=[('yes', u'Si'), ('no', u'No')])
    apostilled_date = fields.Date(string="Fecha de apostillado")
    egress_date = fields.Date(string="Fecha de egreso estimada")
    issue_title_date = fields.Date(string="Fecha de expedición título")
    is_require_thesis = fields.Boolean(string="¿Su estudio requiere o requirió tesis?")
    state_thesis = fields.Selection(string=u'Estado de la tesis',
                                    selection=[('no_starting', u'Sin comenzar'), ('in_progress', u'En curso'),
                                               ('completed', u'Finalizado')])
    title_thesis = fields.Text(string="Título de la tesis")
    description_thesis = fields.Text(string="Describa su tesis")
    tutor = fields.Char(string="Tutor")
    knowledge_thesis_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_thesis_id',
                                            string=u'Conocimientos aplicados a su tesis',
                                            ondelete='restrict',
                                            help='Sólo se pueden seleccionar 5 tipos de conocimientos')
    final_note_thesis = fields.Float(string="Nota final de tesis")
    max_note_thesis = fields.Float(string="Nota máxima posible de tesis")
    scholarship = fields.Float(string="Escolaridad", required=False)
    max_scholarship = fields.Float(string="Escolaridad máxima posible")
    credits_far = fields.Float(string="Créditos / Materias aprobadas hasta el momento")
    credits_training = fields.Float(string="Créditos / Materias totales de la formación")
    area_related_education_ids = fields.One2many('onsc.cv.area.related.education', 'advanced_formation_id',
                                                 string=u'Áreas relacionadas con esta educación', copy=True)
    other_relevant_information = fields.Text(string="Otra información relevante")
    egress_certificate_file = fields.Binary(string="Certificado de egreso / título")
    egress_certificate_filename = fields.Char('Nombre del documento digital - Certificado de egreso / título')

    # FIXME 28.8.3 PS07 13857
    scolarship_certificate_file = fields.Binary(string="Escolaridad")
    scolarship_certificate_filename = fields.Char('Nombre del documento digital - Escolaridad')

    revalidated_certificate_file = fields.Binary(string="Certificado de reválida de título",
                                                 help="Certificado de reválida de título / Resolución de reválida de título / Titulo revalidado")
    revalidated_certificate_filename = fields.Char('Nombre del documento digital - Certificado de reválida de título')
    homologated_certificate_file = fields.Binary(string="Certificado de homologación")
    homologated_certificate_filename = fields.Char('Nombre del documento digital - Certificado de homologación')
    apostille_file = fields.Binary(string="Apostilla")
    apostille_filename = fields.Char('Nombre del documento digital - Apostilla')

    country_code = fields.Char(related="country_id.code")

    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_acquired_advanced_formation_rel',
                                              string=u'Conocimientos adquiridos',
                                              copy=True,
                                              required=True,
                                              ondelete='restrict',
                                              store=True)
    show_generic_academic_program = fields.Boolean('Ver programa academico genreico',
                                                   compute='_compute_show_generic_academic_program')
    name_generic_academic_program = fields.Char('Nombre específico del programa académico')
    generic_academic_program_id = fields.Many2one('onsc.cv.generic.academic.program',
                                                  string=u'Programa académico genérico')
    # UTILITARIO PARA USAR EN VISTA TREE
    displayed_academic_program = fields.Char(
        string='Programa académico',
        store=True,
        compute='_compute_displayed_academic_program')

    @api.depends('institution_id')
    def _compute_show_generic_academic_program(self):
        for record in self:
            record.show_generic_academic_program = record.institution_id.is_without_academic_program

    @api.depends('generic_academic_program_id', 'academic_program_id')
    def _compute_displayed_academic_program(self):
        for rec in self:
            if rec.show_generic_academic_program and rec.generic_academic_program_id:
                rec.displayed_academic_program = rec.generic_academic_program_id.display_name
            else:
                rec.displayed_academic_program = rec.academic_program_id.display_name

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
            self.state_thesis = False
            self.title_thesis = False
            self.description_thesis = False
            self.final_note_thesis = float(0)
            self.final_note_thesis = float(0)
            self.tutor = False
            self.knowledge_thesis_ids = [(5,)]

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

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id and not self.institution_id.is_without_academic_program:
            self.generic_academic_program_id = False
            self.name_generic_academic_program = False
        super(ONSCCVFormationAdvanced, self).onchange_institution_id()

    def _get_json_dict(self):
        json_dict = super(ONSCCVFormationAdvanced, self)._get_json_dict()
        json_dict.extend([
            "homologated_title",
            "homologated_title_date",
            "apostilled_title",
            "apostilled_date",
            "egress_date",
            "issue_title_date",
            "start_date",
            "end_date",
            "is_require_thesis",
            "state_thesis",
            "title_thesis",
            "description_thesis",
            "tutor",
            "final_note_thesis",
            "max_note_thesis",
            "scholarship",
            "max_scholarship",
            "credits_far",
            "credits_training",
            "other_relevant_information",
            "state",
            "conditional_validation_state",
            "conditional_validation_reject_reason",
            ("country_id", ['id', 'name']),
            ("institution_id", ['id', 'name']),
            ("subinstitution_id", ['id', 'name']),
            ("advanced_study_level_id", ['id', 'name']),
            ("academic_program_id", ['id', 'name']),
            ("knowledge_thesis_ids", ['id', 'name']),
            ("area_related_education_ids", self.env['onsc.cv.area.related.education']._get_json_dict()),
            ("knowledge_acquired_ids", ['id', 'name']),
            ("generic_academic_program_id", ['id', 'name']),
            "name_generic_academic_program",
        ])
        return json_dict


class ONSCCVAreaRelatedEducation(models.Model):
    _name = 'onsc.cv.area.related.education'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Área relacionada con esta educación'
    _no_create_ifautosave = True

    advanced_formation_id = fields.Many2one('onsc.cv.advanced.formation',
                                            string=u'Formación avanzada',
                                            ondelete='cascade')
