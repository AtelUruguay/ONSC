# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

TYPES = [('publication', 'Publicación '), ('productions', 'Producciones '), ('evaluation', 'Evaluación'),
         ('other', 'Otro')]


class ONSCCVDigitalPPEvaluations(models.Model):
    _name = 'onsc.cv.publication.production.evaluation'
    _inherit = ['onsc.cv.abstract.documentary.validation']
    _description = 'Publicación, Producción y Evaluación'
    _order = 'date desc'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade', required=True)
    type = fields.Selection(TYPES, string='Tipo', required=True)
    subtype = fields.Char(string="Sub tipo", compute='_compute_subtype', store=True)
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
    is_arbitrated = fields.Boolean(compute='_compute_is_subtype_publication')
    paid_activity = fields.Selection(string=u'¿Actividad remunerada?', required=True,
                                     selection=[('yes', u'Si'), ('no', u'No')])
    authors_ids = fields.One2many('onsc.cv.authors', 'publications_productions_evaluations_id', string=u'Autores',
                                  copy=True)
    activity_area_ids = fields.One2many('onsc.cv.activity.area', 'publications_productions_evaluations_id',
                                        string=u'Área de Actividad', copy=True)
    applied_knowledge_ids = fields.Many2many('onsc.cv.knowledge', 'applied_knowledge_id',
                                             string=u'Conocimientos aplicados', copy=True)
    additional_information = fields.Text(string="Información adicional")

    @api.depends('type', 'subtype_publication_id', 'subtype_production_id', 'subtype_evaluation_id', 'subtype_other_id')
    def _compute_subtype(self):
        for record in self:
            if record.type == 'publication':
                record.subtype = record.subtype_publication_id.display_name
            elif record.type == 'productions':
                record.subtype = record.subtype_production_id.display_name
            elif record.type == 'evaluation':
                record.subtype = record.subtype_evaluation_id.display_name
            if record.type == 'other':
                record.subtype = record.subtype_other_id.display_name

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
            self.subtype_evaluation_id = False
            self.subtype_publication_id = False
            self.subtype_production_id = False
            self.subtype_other_id = False

    @api.onchange('applied_knowledge_ids')
    def onchange_knowledge_key_insights_ids(self):
        if len(self.applied_knowledge_ids) > 5:
            self.applied_knowledge_ids = self.applied_knowledge_ids[:5]
            return cv_warning(_("Sólo se pueden seleccionar 5 tipos de conocimientos"))

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalPPEvaluations, self)._get_json_dict()
        json_dict.extend([
            "type",
            "other_subtype_publication",
            "other_subtype_production",
            "other_subtype_evaluation",
            "other_subtype_other",
            "date",
            "tittle",
            "description",
            "location",
            "arbitrated",
            "paid_activity",
            "additional_information",
            ("subtype_publication_id", ['id', 'name']),
            ("subtype_production_id", ['id', 'name']),
            ("subtype_evaluation_id", ['id', 'name']),
            ("subtype_other_id", ['id', 'name']),
            ("authors_ids", self.env['onsc.cv.authors']._get_json_dict()),
            ("activity_area_ids", self.env['onsc.cv.activity.area']._get_json_dict()),
            ("applied_knowledge_ids", ['id', 'name'])
        ])
        return json_dict


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

    def _get_json_dict(self):
        return [
            "author",
            "citation",
            "is_primary_author"
        ]


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

    @api.model
    def create(self, values):
        _publications_productions_evaluations_id = values.get('publications_productions_evaluations_id')
        _educational_area_id = values.get('educational_area_id')
        _educational_subarea_id = values.get('educational_subarea_id')
        _discipline_educational_id = values.get('discipline_educational_id')
        args = [
            ('educational_area_id', '=', _educational_area_id),
            ('educational_subarea_id', '=', _educational_subarea_id),
            ('discipline_educational_id', '=', _discipline_educational_id)
        ]
        if values.get('publications_productions_evaluations_id'):
            args.append(('publications_productions_evaluations_id', '=', _publications_productions_evaluations_id))
        else:
            args.append(('participation_events_id', '=', values.get('participation_events_id')))

        all_values_tocheck = _educational_area_id and _educational_subarea_id and _discipline_educational_id
        if all_values_tocheck and self.search_count(args):
            return self
        return super(ONSCCVActivityArea, self).create(values)

    def _get_json_dict(self):
        json_dict = super(ONSCCVActivityArea, self)._get_json_dict()
        json_dict.extend([
            "speciality"
        ])
        return json_dict
