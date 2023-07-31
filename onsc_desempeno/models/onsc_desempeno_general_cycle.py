# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoGeneralCycle(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _description = u'Ciclo General de Evaluación de Desempeño'


    year = fields.Integer(u'Año')
    start_date = fields.Date(string=u'Fecha inicio')
    end_date = fields.Date(string=u'Fecha fin')
    start_date_max = fields.Date(string=u'Fecha inicio máx.')
    end_date_max = fields.Date(string=u'Fecha fin máx.')
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('year_uniq', 'unique(year)', u'Solo se puede tener una configuración para el año'),
    ]

    @api.constrains("start_date", "end_date", "start_date_max", "end_date_max")
    def _check_date(self):
        for record in self:
            if record.start_date <= record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.start_date > fields.Date.today():
                raise ValidationError(_(u"La fecha inicio debe ser mayor o igual a la fecha actual"))
            if record.start_date_max <= record.end_date_max:
                raise ValidationError(_(u"La fecha inicio máxima debe ser menor o igual a la fecha de fin máxima"))
            if record.start_date_max > record.start_date:
                raise ValidationError(_(u"La fecha inicio máxima debe ser mayor o igual a la fecha de inicio"))
            if record.end_date_max <= record.end_date:
                raise ValidationError(_(u"La fecha fin máxima debe ser menor o igual a la fecha de fin "))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['year'] = _("%s (Copia)") % self.year
        return super(ONSCDesempenoGeneralCycle, self).copy(default=default)
