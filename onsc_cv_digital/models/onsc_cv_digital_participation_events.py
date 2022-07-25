# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning

MODES = [('face_to_face', 'Presencial'), ('virtual', 'Virtual'), ('hybrid', 'Híbrido')]


class ONSCCVDigitalParticipationEvent(models.Model):
    _name = 'onsc.cv.participation.event'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.conditional.state']
    _description = 'Participación en evento'
    _order = 'start_date desc'

    name_event = fields.Char(string=u"Nombre del evento", required=True)
    type_event_id = fields.Many2one('onsc.cv.type.event', string=u'Tipo de evento', ondelete='cascade')
    mode = fields.Selection(MODES, u'Modalidad', required=True)
    country_id = fields.Many2one("res.country", string=u"País del evento", required=True)
    city_id = fields.Many2one("onsc.cv.location", string=u"Ciudad")
    name_institution = fields.Char(string=u"Nombre de institución organizadora", required=True)
    description_event = fields.Text(string=u"Descripción del evento")
    roll_event_id = fields.Many2one('onsc.cv.roll.event', string=u'Rol en evento', required=True, ondelete='cascade')
    is_roll_event = fields.Boolean(compute='_compute_is_roll_event')
    description_topic = fields.Char(string=u"Descripción de la temática abordada ")
    hourly_load = fields.Float('Carga horaria (en horas)')
    hours_total = fields.Float('Carga horaria total (en horas)', required='True')
    activity_area_ids = fields.One2many('onsc.cv.activity.area', 'participation_events_id', string=u'Área de Actividad')
    documentation_file = fields.Binary(string="Documentación o comprobantes", required=True)
    documentation_filename = fields.Char('Nombre documentación o comprobantes')

    @api.depends('roll_event_id')
    def _compute_is_roll_event(self):
        roll_event_exhibitor_id = self.env.ref('onsc_cv_digital.onsc_cv_roll_event_exhibitor').id
        roll_event_moderator_id = self.env.ref('onsc_cv_digital.onsc_cv_roll_event_moderator').id
        roll_event_commentator_id = self.env.ref('onsc_cv_digital.onsc_cv_roll_event_commentator').id
        roll_event_panelist_id = self.env.ref('onsc_cv_digital.onsc_cv_roll_event_panelist').id
        roll_event_speaker_quest_id = self.env.ref('onsc_cv_digital.onsc_cv_roll_event_speaker_quest').id
        roll_event_list = [roll_event_exhibitor_id, roll_event_moderator_id, roll_event_commentator_id,
                           roll_event_panelist_id, roll_event_speaker_quest_id]
        for record in self:
            if record.roll_event_id.id in roll_event_list:
                record.is_roll_event = True
            else:
                record.is_roll_event = False
