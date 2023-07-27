# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoReasonChangeEvaluator(models.Model):
    _name = 'onsc.desempeno.reason.change.evaluator'
    _description = 'Motivos cambio de evaluador'

    name = fields.Char(string="Nombre del motivo del cambio de evaluador", required=True)
    agree = fields.Boolean(string="No Acuerdo")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del nivel debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoReasonChangeEvaluator, self).copy(default=default)
