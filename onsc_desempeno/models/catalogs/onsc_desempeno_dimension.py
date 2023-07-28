# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoDimension(models.Model):
    _name = 'onsc.desempeno.dimension'
    _description = 'Dimensiones'

    name = fields.Char(string="Nombre de la dimensión", required=True)
    definition = fields.Text(string="Definición")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la dimensión debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoDimension, self).copy(default=default)
