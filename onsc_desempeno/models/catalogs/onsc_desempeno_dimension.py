# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoDimension(models.Model):
    _name = 'onsc.desempeno.dimension'
    _description = 'Dimensiones'

    name = fields.Char(string="Dimensiones", required=True)
    definition = fields.Char(string="Definición de dimensión")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la dimensión debe ser único'),
    ]

    def toggle_active(self):
        return super(ONSCDesempenoDimension, self.with_context(no_check_write=True)).toggle_active()
