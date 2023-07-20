# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoLevel(models.Model):
    _name = 'onsc.desempeno.level'
    _description = 'Niveles'

    name = fields.Char(string="Niveles", required=True)
    definition = fields.Char(string="Definición del nivel")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del nivel debe ser único'),
    ]

    def toggle_active(self):
        return super(ONSCDesempenoLevel, self.with_context(no_check_write=True)).toggle_active()


class OperatingUnit(models.Model):
    _inherit = ['onsc.catalog.occupation']
    _name = 'onsc.catalog.occupation'

    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel de requerimiento")
