# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVFormationBasic(models.Model):
    _name = 'onsc.cv.basic.formation'
    _description = 'Formación básica'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _order = 'start_date desc'
    _catalogs2validate = ['institution_id', 'subinstitution_id']

    basic_education_level = fields.Selection(string=u'Nivel de estudios básicos',
                                             selection=[('primary', u'Primaria'),
                                                        ('secondary', u'Secundaria'),
                                                        ('utu', u'UTU')], required=True)
    coursed_years = fields.Text(string="Años cursados")
    study_certificate_file = fields.Binary(string="Certificado de estudio", required=True)
    study_certificate_name = fields.Char(string="Nombre certificado de estudio")


class ONSCCVFormationAdvanced(models.Model):
    _name = 'onsc.cv.advanced.formation'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.institution', 'onsc.cv.abstract.conditional.state']
    _description = 'Formación avanzada'
    _catalogs2validate = ['institution_id', 'subinstitution_id']

    advanced_study_level_id = fields.Many2one('onsc.cv.study.level', string=u'Nivel de estudio avanzado', required=True)
    academic_program_id = fields.Many2one('onsc.cv.academic.program', string=u'Programa académico', required=True)
    homologated_title = fields.Selection(string=u'¿Su título esta revalidado/homologado en Uruguay?',
                                         selection=[('yes', u'Si'), ('no', u'No')])
    homologated_title_date = fields.Date(string="Fecha de revalidación",
                                         help='Fecha de revalidación/homologación de título')
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
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', 'knowledge_acquired_formation_rel',
                                              store=True, string=u'Conocimientos adquiridos', required=True,
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

    country_code = fields.Char(related="country_id.code")

    @api.onchange('egress_date')
    def onchange_egress_date(self):
        if self.start_date and self.egress_date and self.egress_date <= self.start_date:
            self.egress_date = self.start_date

    @api.onchange('state', 'is_require_thesis')
    def onchange_state_is_require_thesis(self):
        if self.state == 'completed' and self.is_require_thesis:
            self.state_thesis = 'completed'
        else:
            self.state_thesis = ''


class ONSCCVAreaRelatedEducation(models.Model):
    _name = 'onsc.cv.area.related.education'
    _description = 'Área relacionada con esta educación'

    advanced_formation_id = fields.Many2one('onsc.cv.advanced.formation', string=u'Formación avanzada')
    educational_areas_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área de educación', required=True)
    educational_subareas_id = fields.Many2one('onsc.cv.educational.subarea', string=u'Sub área de educación',
                                              required=True)
    discipline_educational_id = fields.Many2one('onsc.cv.discipline.educational', string=u'Disciplina de educación',
                                                required=True)
