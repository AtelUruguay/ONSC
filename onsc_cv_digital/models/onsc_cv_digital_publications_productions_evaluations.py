# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

TYPES = [('publication', 'Publicación '), ('productions', 'Producciones '), ('evaluation', 'Evaluación'),
         ('other', 'Otro')]


class ONSCCVDigitalPPEvaluations(models.Model):
    _name = 'onsc.cv.publication.production.evaluation'
    _description = 'Publicación, Producción y Evaluación'
    _order = 'date desc'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade', required=True)
    type = fields.Selection(TYPES, string='Tipo', required=True)
    subtype_publication_id = fields.Many2one("onsc.cv.subtype.publication", 'Sub tipo de publicación')
    other_subtype_publication = fields.Char(string=u"Otro sub tipo de publicación")
    is_subtype_publication = fields.Boolean(related="subtype_publication_id.is_option_other_enable")
    subtype_production_id = fields.Many2one("onsc.cv.subtype.production", 'Sub tipo de producción')
    other_subtype_production = fields.Char(string=u"Otro sub tipo de producción")
    is_subtype_production = fields.Boolean(related="subtype_production_id.is_option_other_enable")
    subtype_evaluation_id = fields.Many2one("onsc.cv.subtype.evaluation", 'Sub tipo de evaluación')
    other_subtype_evaluation = fields.Char(string=u"Otro sub tipo de evaluación")
    is_subtype_evaluation = fields.Boolean(related="subtype_evaluation_id.is_option_other_enable")
    subtype_other_id = fields.Many2one("onsc.cv.subtype.other", 'Sub tipo otro')
    other_subtype_other = fields.Char(string=u"Otro sub tipo otro")
    is_subtype_other = fields.Boolean(related="subtype_other_id.is_option_other_enable")
    date = fields.Date(string="Fecha de publicación", required=True)
    tittle = fields.Char(string=u"Título", required=True)
    description = fields.Char(string=u"Descripción", required=True)
    location = fields.Char(string=u"Ubicación")
    arbitrated = fields.Selection(string=u'¿Arbitrado?',
                                  selection=[('yes', u'Si'), ('no', u'No')])
    is_arbitrated = fields.Boolean(string='Activo', compute='_compute_is_subtype_publication')
    paid_activity = fields.Selection(string=u'¿Actividad remunerada?', required=True,
                                     selection=[('yes', u'Si'), ('no', u'No')])
    authors_ids = fields.One2many('onsc.cv.authors', 'publications_productions_evaluations_id', string=u'Autores')
    activity_area_ids = fields.One2many('onsc.cv.activity.area', 'publications_productions_evaluations_id',
                                        string=u'Área de Actividad')
    applied_knowledge_ids = fields.Many2many('onsc.cv.knowledge', 'applied_knowledge_id',
                                             string=u'Conocimientos aplicados')
    additional_information = fields.Text(string="Información adicional")

    @api.depends('subtype_publication_id')
    def _compute_is_subtype_publication(self):
        id_publication_scientific = self.env.ref('onsc_cv_digital.onsc_cv_subtype_publication_scientific_magazine').id
        id_publication_accepted = self.env.ref('onsc_cv_digital.onsc_cv_subtype_publication_accepted').id
        id_publication_event = self.env.ref('onsc_cv_digital.onsc_cv_subtype_publication_event').id
        for record in self:
            if (record.subtype_publication_id.id == id_publication_scientific) or (
                    record.subtype_publication_id.id == id_publication_accepted) or (
                    record.subtype_publication_id.id == id_publication_event):
                record.is_arbitrated = True
            else:
                record.is_arbitrated = False

    @api.onchange('type')
    def onchange_type(self):
        if self.type:
            self.subtype_evaluation_id = ''
            self.subtype_publication_id = ''
            self.subtype_production_id = ''
            self.subtype_other_id = ''

    @api.onchange('applied_knowledge_ids')
    def onchange_knowledge_key_insights_ids(self):
        if len(self.applied_knowledge_ids) > 5:
            self.applied_knowledge_ids = self.applied_knowledge_ids[:5]
            return cv_warning(_("Sólo se pueden seleccionar 5 tipos de conocimientos"))


class ONSCCVAuthors(models.Model):
    _name = 'onsc.cv.authors'
    _description = 'Autor'

    publications_productions_evaluations_id = fields.Many2one('onsc.cv.publication.production.evaluation',
                                                              string=u'Publicación, Producción y Evaluación',
                                                              ondelete='cascade')
    author = fields.Char(string=u"Autor", default=lambda self: self.get_default_author())
    citation = fields.Text(string=u"Citación")
    is_primary_author = fields.Boolean(string=u"Autor principal")

    @api.model
    def get_default_author(self):
        """
        Si en la lista no se ha adicionado el nombre del usuario entonces el valor por defecto
        es el nombre del usuario
        :return:
        """
        authors_ids = self._context.get('authors_ids')
        if not list(filter(lambda x: (x[0] == 0 and x[2]['author'] or x[0] in [1, 4] and self.browse(
                x[1]).author) == self.env.user.name, authors_ids)):
            return self.env.user.name
        return False


class ONSCCVActivityArea(models.Model):
    _name = 'onsc.cv.activity.area'
    _inherit = ['onsc.cv.abstract.formation.line']
    _description = 'Área de Actividad'

    publications_productions_evaluations_id = fields.Many2one('onsc.cv.publication.production.evaluation',
                                                              string=u'Publicación, Producción y Evaluación',
                                                              ondelete='cascade')
    participation_events_id = fields.Many2one('onsc.cv.participation.event',
                                              string=u'Publicación, Producción y Evaluación',
                                              ondelete='cascade')
    speciality = fields.Char(string=u"Especialidad")
