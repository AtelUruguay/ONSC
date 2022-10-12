# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import filter_str2float
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

MODES = [('face_to_face', 'Presencial'), ('virtual', 'Virtual'), ('hybrid', 'Híbrido')]


class ONSCCVDigitalParticipationEvent(models.Model):
    _name = 'onsc.cv.participation.event'
    _inherit = ['onsc.cv.abstract.formation', 'onsc.cv.abstract.conditional.state']
    _catalogs_2validate = ['type_event_id', 'city_id']
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
    description_topic = fields.Char(string=u"Descripción de la temática abordada en el rol")
    hourly_load = fields.Char('Carga horaria en el rol (en horas)')
    hours_total = fields.Char('Carga horaria total del evento (en horas)', required='True')
    activity_area_ids = fields.One2many('onsc.cv.activity.area', 'participation_events_id', string=u'Área de Actividad',
                                        copy=True)
    documentation_file = fields.Binary(string="Documentación o comprobante")
    documentation_filename = fields.Char('Nombre documentación o comprobante')

    @api.onchange('hourly_load')
    def onchange_hourly_load(self):
        try:
            decimal_point = self.env['res.lang'].search([('code', '=', self.env.user.lang)]).decimal_point
            if self.hourly_load:
                if decimal_point == ',':
                    hourly_load = self.hourly_load.replace(',', '.')
                else:
                    hourly_load = self.hourly_load
                self.hourly_load and float(hourly_load)
        except ValueError:
            self.hourly_load = filter_str2float(
                self.hourly_load,
                self.env['res.lang'].search([('code', '=', self.env.user.lang)]).decimal_point
            )
            return cv_warning(_("La Carga horaria en el rol (en horas) no puede contener letras"))

    @api.onchange('hours_total')
    def onchange_hours_total(self):
        try:
            decimal_point = self.env['res.lang'].search([('code', '=', self.env.user.lang)]).decimal_point
            if self.hours_total:
                if decimal_point == ',':
                    hours_total = self.hours_total.replace(',', '.')
                else:
                    hours_total = self.hours_total
                self.hours_total and float(hours_total)
        except ValueError:
            self.hours_total = filter_str2float(
                self.hours_total,
                self.env['res.lang'].search([('code', '=', self.env.user.lang)]).decimal_point)
            return cv_warning(_("La Carga horaria total del evento (en horas) no puede contener letras"))

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

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalParticipationEvent, self)._get_json_dict()
        json_dict.extend([
            "name_event",
            "mode",
            "name_institution",
            "description_event",
            "is_roll_event",
            "description_topic",
            "hourly_load",
            "hours_total",
            ("type_event_id", ['id', 'name']),
            ("country_id", ['id', 'name']),
            ("city_id", ['id', 'name']),
            ("roll_event_id", ['id', 'name']),
            ("activity_area_ids", ['id', 'name']),
        ])
        return json_dict
