# -*- coding: utf-8 -*-
from odoo import Command
from odoo import fields, models

HISTORY_COLUMNS = [
    'start_date',
    'type_event_id',
    'name_event',
    'roll_event_id',
    'country_id',
    'city_id',
    'name_institution',
    'hourly_load',
    'hours_total',
    'mode',
    'conditional_validation_state',
    'end_date',
    'description_event',
    'is_roll_event',
    'description_topic',
    'hourly_load',
    'documentation_file',
    'documentation_filename',
    'other_relevant_information',
]

TREE_HISTORY_COLUMNS = [
    'start_date',
    'type_event_id',
    'name_event',
    'roll_event_id',
    'city_id',
    'name_institution',
]


class ONSCCVDigitalParticipationEvent(models.Model):
    _inherit = 'onsc.cv.participation.event'
    _legajo_model = 'onsc.legajo.participation.event'

    def _update_legajo_record_vals(self, vals):
        if 'activity_area_ids' in vals:
            vals['activity_area_ids'] = [Command.clear()] + vals['activity_area_ids']
        return vals


class ONSCLegajoParticipationEvent(models.Model):
    _name = 'onsc.legajo.participation.event'
    _inherit = ['onsc.cv.participation.event', 'model.history']
    _description = 'Legajo - Participación en evento'
    _history_model = 'onsc.legajo.participation.event.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.participation.event",
        string=u"Participación en evento origen",
        ondelete="set null"
    )

    activity_area_ids = fields.One2many('onsc.legajo.activity.area',
                                        'legajo_participation_events_id',
                                        string=u'Área de Actividad', )

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_participation_event_form').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoActivityArea(models.Model):
    _name = 'onsc.legajo.activity.area'
    _inherit = 'onsc.cv.activity.area'
    _description = 'Legajo - Área de Actividad'

    legajo_participation_events_id = fields.Many2one(
        'onsc.legajo.participation.event',
        string=u'Participación en eventos',
        ondelete='cascade')
    legajo_publications_productions_evaluations_id = fields.Many2one(
        'onsc.legajo.publication.production.evaluation',
        'Tutorías, Orientaciones, Supervisiones',
        ondelete='cascade',
        required=False)


class ONSCLegajoParticipationEventHistory(models.Model):
    _name = 'onsc.legajo.participation.event.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.participation.event'

    history_documentation_file = fields.Binary(string="Documentación o comprobante")
