# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoReasonChangeEvaluator(models.Model):
    _name = 'onsc.desempeno.reason_change_evaluator'
    _description = 'Motivos de cambio de evaluador'

    name = fields.Char(string="Motivos de cambio de evaluador ", required=True)
    agree = fields.Boolean(string="No Acuerdo")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del nivel debe ser único'),
    ]

    def toggle_active(self):
        return super(ONSCDesempenoReasonChangeEvaluator, self.with_context(no_check_write=True)).toggle_active()
