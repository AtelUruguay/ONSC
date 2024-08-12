# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCLegajoSynconizeWS7Wizard(models.TransientModel):
    _name = 'onsc.legajo.syncronize.ws7.wizard'
    _description = 'Sincronizar WS 7'

    end_datetime = fields.Datetime(string="Fecha/hora hasta", required=True)
    start_datetime = fields.Datetime(string="Fecha/hora desde", required=True)

    def action_sycronize(self):
        WS7 = self.env['onsc.legajo.abstract.ws7'].suspend_security()
        WS7.with_context(wizard=True).syncronize(fecha_hasta=self.end_datetime, fecha_desde=self.start_datetime)

    @api.constrains('start_datetime', 'end_datetime')
    def _check_start_date_end_date(self):
        if self.start_datetime and self.end_datetime and self.end_datetime < self.start_datetime:
            raise ValidationError(_(u"La fecha desde no puede ser mayor que la fecha hasta"))
