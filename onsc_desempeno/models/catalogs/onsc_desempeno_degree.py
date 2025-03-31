# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoDegree(models.Model):
    _name = 'onsc.desempeno.degree'
    _description = 'Equivalencia de Grado de necesidad de desarrollo'

    name = fields.Char(string="Nombre-Frecuencia del comportamiento", compute="_compute_name", store=True)
    description = fields.Char(string="Nombre de la necesidad de desarrollo", required=True)
    frecuency = fields.Char(string="Frecuencia de comportamiento", required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('description_uniq', 'unique(description)', u'El nombre del grado de desarrollo debe ser único'),
    ]

    @api.depends('description', 'frecuency')
    def _compute_name(self):
        for record in self:
            if record.description and record.frecuency:
                record.name = '%s - %s' % (record.description, record.frecuency)
            else:
                record.name = ''

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['description'] = _("%s (Copia)") % self.description
        return super(ONSCDesempenoDegree, self).copy(default=default)
