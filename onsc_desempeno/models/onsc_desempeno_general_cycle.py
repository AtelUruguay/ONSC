# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoGeneralCycle(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _description = u'Ciclo general de evaluación de desempeño'
    _rec_name = 'year'

    year = fields.Integer(u'Año', required=True)
    start_date = fields.Date(string=u'Fecha inicio', required=True)
    end_date = fields.Date(string=u'Fecha fin', required=True)
    start_date_max = fields.Date(string=u'Fecha inicio máx.', required=True)
    end_date_max = fields.Date(string=u'Fecha fin máx.', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('year_uniq', 'unique(year)', u'Solo se puede tener una configuración para el año'),
    ]

    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if record.start_date < fields.Date.today():
                raise ValidationError(_("La fecha inicio debe ser mayor o igual a la fecha actual"))

    @api.constrains("start_date", "end_date", "start_date_max", "end_date_max", "year")
    def _check_date(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.start_date_max > record.end_date_max:
                raise ValidationError(_(u"La fecha inicio máxima debe ser menor o igual a la fecha de fin máxima"))
            if record.start_date_max < record.start_date:
                raise ValidationError(_(u"La fecha inicio máxima debe ser mayor o igual a la fecha de inicio"))
            if record.end_date_max >= record.end_date:
                raise ValidationError(_(u"La fecha fin máxima debe ser menor o igual a la fecha de fin "))
            if int(record.start_date.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha inicio debe  estar dentro del año %s") % record.year)
            if int(record.end_date.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha fin debe  estar dentro del año %s") % record.year)
            if int(record.end_date_max.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha fin máxima debe  estar dentro del año %s") % record.year)
            if int(record.start_date_max.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha inicio máxima debe  estar dentro del año %s") % record.year)

            evaluations_qty = self.env['onsc.desempeno.evaluation.stage'].suspend_security().search_count(
                [("general_cycle_id", "=", record.id), ("start_date", "=", record.start_date_max),
                 ("start_date", "=", record.start_date), ("end_date", "=", record.end_date_max)])
            if evaluations_qty > 0:
                raise ValidationError(
                    _(u"No se cumple las condiciones de la etapa de evaluaciones 360° por UE "
                      u"que esta asociada a ciclo general de evaluación de desempeño"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['year'] = _("%s (Copia)") % self.year
        return super(ONSCDesempenoGeneralCycle, self).copy(default=default)

    def disable_evaluation(self):
        self.search([('end_date', '<', fields.Date.today())]).write({'active': False})
        self.env['onsc.desempeno.evaluation.stage'].suspend_security().search(
            [('end_date', '<', fields.Date.today())]).write({'active': False, 'closed_stage': True})
