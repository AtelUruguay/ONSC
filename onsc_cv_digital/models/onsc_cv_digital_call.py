# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCCVDigitalCall(models.Model):
    _name = 'onsc.cv.digital.call'
    _inherits = {'onsc.cv.digital': 'cv_digital_id'}
    _description = 'Llamado'
    _rec_name = 'cv_full_name'

    cv_digital_id = fields.Many2one(
        "onsc.cv.digital",
        string="CV",
        auto_join=True,
        required=True, index=True)

    call_number = fields.Char(string=u"Llamado", required=True, index=True)
    postulation_date = fields.Datetime(string=u"Fecha de postulación", required=True, index=True)
    postulation_number = fields.Integer(string=u"Número de postulación", required=True, index=True)
    is_json_sent = fields.Boolean(string="Copia enviada")
    is_cancel = fields.Boolean(string="Cancelado")
    is_zip = fields.Boolean(string="ZIP generado")
    is_trans = fields.Boolean(string=u"Personas Trans (Art.12 Ley N° 19.684)")
    is_afro = fields.Boolean(string=u"Afrodescendientes (Art.4 Ley N° 19122)")
    is_disabilitie = fields.Boolean(string=u"Persona con Discapacidad (Art. 49 Ley N° 18.651)")
    is_victim = fields.Boolean(string=u"Personas víctimas de delitos violentos (Art. 105 Ley N° 19.889)")
    preselected = fields.Selection(string="Preseleccionado", selection=[('yes', 'Si'), ('no', 'No')])

    @api.constrains("cv_digital_id", "cv_digital_id.active", "call_number")
    def _check_cv_call_unicity(self):
        for record in self.filtered(lambda x: x.active):
            if self.search_count([('cv_digital_id.active', '=', True),
                                  ('call_number', '=', record.call_number),
                                  ('id', '!=', record.id)]):
                raise ValidationError(
                    _(u"El llamado ya se encuentra activo en el sistema")
                )

    def init(self):
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS onsc_cv_digital_call_call_number_postulation_date_postulation_number
                                    ON onsc_cv_digital_call (call_number, postulation_date,postulation_number)
        """)

    @api.model
    def create(self, values):
        values['type'] = 'call'
        result = super(ONSCCVDigitalCall, self).create(values)
        return result
