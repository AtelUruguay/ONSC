# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.development_means'
    _description = 'Medios de desarrollo'

    name = fields.Char(string="Medios de desarrollo", requiered=True)
    description = fields.String(string="Descripción")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name")', u'El nombre del medios de desarrollo debe ser único'),
    ]

    def toggle_active(self):
        return super(ONSCDesempenoDevelopmentMeans, self.with_context(no_check_write=True)).toggle_active()
