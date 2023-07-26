# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.development.means'
    _description = 'Medios de desarrollo'

    name = fields.Char(string="Nombre del medio de desarrollo", required=True)
    description = fields.Char(string="Descripción")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del medios de desarrollo debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoDevelopmentMeans, self).copy(default=default)
    def toggle_active(self):
        return super(ONSCDesempenoDevelopmentMeans, self.with_context(no_check_write=True)).toggle_active()
