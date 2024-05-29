# -*- coding: utf-8 -*-

from odoo import Command
from odoo import fields, models

POSTGRADUATE_TYPES = [('academic', 'Académico'), ('professional', 'Profesional')]
HISTORY_COLUMNS = [
    'type',
    'subtype_publication_id',
    'other_subtype_publication',
    'subtype_production_id',
    'other_subtype_production',
    'subtype_evaluation_id',
    'date',
    'other_subtype_evaluation',
    'subtype_other_id',
    'other_subtype_other',
    'tittle',
    'description',
    'location',
    'arbitrated',
    'paid_activity',
    'additional_information',
    'subtype',
    'applied_knowledge_ids'
]

TREE_HISTORY_COLUMNS = {
    'date': 'Fecha',
    'type': 'Tipo',
    'subtype': 'Sub tipo',
    'tittle': 'Título',
}


class ONSCCVPublicationProductionEvaluation(models.Model):
    _inherit = 'onsc.cv.publication.production.evaluation'
    _legajo_model = 'onsc.legajo.publication.production.evaluation'

    def _update_legajo_record_vals(self, vals):
        if 'authors_ids' in vals:
            vals['authors_ids'] = [Command.clear()] + vals['authors_ids']
        if 'applied_knowledge_ids' in vals:
            vals['applied_knowledge_ids'] = [Command.clear()] + vals['applied_knowledge_ids']
        if 'activity_area_ids' in vals:
            vals['activity_area_ids'] = [Command.clear()] + vals['activity_area_ids']
        return vals


class ONSCLegajoPublicationProductionEvaluation(models.Model):
    _name = 'onsc.legajo.publication.production.evaluation'
    _description = 'Legajo - Publicación, Producción y Evaluación'
    _inherit = ['onsc.cv.publication.production.evaluation', 'model.history']
    _history_model = 'onsc.legajo.publication.production.evaluation.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS
    _order = 'date desc'

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one("onsc.cv.publication.production.evaluation",
                                       string=u"Publicación, Producción y Evaluación",
                                       ondelete="set null")

    is_arbitrated = fields.Boolean('¿Arbitrado?', history=True)
    subtype = fields.Char(string="Sub tipo", history=True)
    is_subtype_publication = fields.Boolean(string="Es otro sub tipo de publicación?", history=True)
    is_subtype_production = fields.Boolean(string="Es otro sub tipo de producción?", history=True)
    is_subtype_evaluation = fields.Boolean(string="Es otro sub tipo de evaluación?", history=True)
    is_subtype_other = fields.Boolean(string="Es otro sub tipo otro?", history=True)

    authors_ids = fields.One2many('onsc.legajo.authors', 'legajo_publications_productions_evaluations_id',
                                  string=u'Autores',
                                  copy=True)
    activity_area_ids = fields.One2many('onsc.legajo.activity.area', 'legajo_publications_productions_evaluations_id',
                                        string=u'Área de Actividad', copy=True)
    applied_knowledge_ids = fields.Many2many(
        'onsc.cv.knowledge',
        'legajo_applied_knowledge_id',
        string=u'Conocimientos aplicados',
        ondelete='restrict',
        copy=True)

    def button_show_history(self):
        model_view_form_id = self.env.ref(
            'onsc_cv_digital_legajo.onsc_legajo_publication_production_evaluation_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoAuthors(models.Model):
    _name = 'onsc.legajo.authors'
    _inherit = ['onsc.cv.authors']
    _description = 'Legajo -  Autores'

    legajo_publications_productions_evaluations_id = fields.Many2one(
        'onsc.legajo.publication.production.evaluation',
        'Tutorías, Orientaciones, Supervisiones',
        ondelete='cascade',
        required=True)


# class ONSCLegajoAuthors(models.Model):
#     _name = 'onsc.legajo.activity.area'
#     _inherit = ['onsc.cv.activity.area']
#     _description = 'Legajo -  Área de Actividad'


# HISTORICO
class ONSCLegajoPublicationProductionEvaluationHistory(models.Model):
    _name = 'onsc.legajo.publication.production.evaluation.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.publication.production.evaluation'
