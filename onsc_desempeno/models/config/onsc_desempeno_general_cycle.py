# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCDesempenoDegree(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _description = 'Ciclo General de Evaluación de Desempeño'

    year = fields.Integer(u'Año')
    start_date = fields.Date(string=u'Fecha inicio')
    end_date = fields.Date(string=u'Fecha fin')
    start_date_max = fields.Date(string=u'Fecha inicio máx.')
    end_date_max = fields.Date(string=u'Fecha fin máx.')
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('year_uniq', 'unique(year)', u'Solo se puede tener una configuración para el año'),
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

    def toggle_active(self):
        return super(ONSCDesempenoDegree, self.with_context(no_check_write=True)).toggle_active()
