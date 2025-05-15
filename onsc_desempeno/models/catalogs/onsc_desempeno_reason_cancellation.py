# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoReasonCancellation(models.Model):
    _name = 'onsc.desempeno.reason.cancellation'
    _description = 'Catalogo Motivos de cancelación de formularios'

    name = fields.Char(string="Motivo de cancelación", required=True)
    description = fields.Text(string="Descripción")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El Motivos de cancelación debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoReasonCancellation, self).copy(default=default)
