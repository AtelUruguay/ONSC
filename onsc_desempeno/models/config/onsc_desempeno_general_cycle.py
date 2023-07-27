# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoGeneralCycle(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _description = 'Ciclo General de Evaluación de Desempeño'
    _rec_name = 'year'

    year = fields.Integer(u'Año')
    start_date = fields.Date(string=u'Fecha inicio')
    end_date = fields.Date(string=u'Fecha fin')
    start_date_max = fields.Date(string=u'Fecha inicio máx.')
    end_date_max = fields.Date(string=u'Fecha fin máx.')
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('year_uniq', 'unique(year)', u'Solo se puede tener una configuración para el año'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['year'] = _("%s (Copia)") % self.year
        return super(ONSCDesempenoGeneralCycle, self).copy(default=default)

    def toggle_active(self):
        return super(ONSCDesempenoGeneralCycle, self.with_context(no_check_write=True)).toggle_active()
