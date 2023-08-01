# -*- coding: utf-8 -*-
import datetime
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoGeneralCycle(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _description = u'Ciclo General de Evaluación de Desempeño'
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

    @api.constrains("start_date", "end_date", "start_date_max", "end_date_max")
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

    @api.onchange('start_date')
    def onchange_start_date(self):
        Evaluation = self.env['onsc.desempeno.evaluation.stage'].suspend_security().search(
            [("general_cycle_id", "=", self.id)])
        if Evaluation:
            if Evaluation.start_date > self.start_date_max:
                raise ValidationError(
                    _(u"La fecha inicio maxima debe ser menor o igual a la fecha de inicio de la evaluacion ya existente"))
            if Evaluation.start_date < self.start_date:
                raise ValidationError(
                    _(u"La fecha inicio debe ser menor o igual a la fecha de inicio de la evaluacion ya existente"))
            if Evaluation.end_date > self.end_date_max:
                raise ValidationError(
                    _(u"La fecha fin maxima debe ser mayor o igual a la fecha de fin de la evaluacion ya existente"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['year'] = _("%s (Copia)") % self.year
        return super(ONSCDesempenoGeneralCycle, self).copy(default=default)

    def disable_evaluation(self):
        for record in self.search([('end_date', '<', fields.Date.today())]):
            record.write({'active': False})
        for record in self.env('onsc.desempeno.evaluation.stage').suspend_security().search(
                [('end_date', '<', fields.Date.today())]):
            record.write({'active': False, 'closed_stage': True})

    def write(self, vals):
        if vals.get('start_date') and datetime.datetime.strptime(vals.get('start_date'),
                                                                 '%Y-%m-%d').date() < fields.Date.today():
            raise ValidationError(_("Solo puede editar si la fecha inicio es mayor a la fecha actual"))
        return super(ONSCDesempenoGeneralCycle, self).write(vals)

    @api.model
    def create(self, vals):
        if datetime.datetime.strptime(vals.get('start_date'), '%Y-%m-%d').date() < fields.Date.today():
            raise ValidationError(_("Solo puede crear si la fecha inicio es mayor a la fecha actual"))
        return super(ONSCDesempenoGeneralCycle, self).create(vals)
