# -*- coding: utf-8 -*-
import datetime
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluationStage(models.Model):
    _name = 'onsc.desempeno.evaluation.stage'
    _description = u'Etapa de evaluaciones 360° por UE'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluationStage, self)._search(args, offset=offset, limit=limit, order=order,
                                                                 count=count,
                                                                 access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def default_get(self, fields):
        res = super(ONSCDesempenoEvaluationStage, self).default_get(fields)
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        res['operating_unit_id'] = operating_unit_id.id

        return res

    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string=u'Año', domain=[("active", "=", True)], )
    start_date = fields.Date(string=u'Fecha inicio')
    end_date_environment = fields.Date(string=u'Fecha fin def. entorno')
    end_date = fields.Date(string=u'Fecha fin')
    active = fields.Boolean(string="Activo", default=True)
    closed_stage = fields.Boolean(string="Etapa cerrada", default=False)
    show_buttons = fields.Boolean(string="Editar datos de contrato", compute='_compute_show_buttons')
    is_edit_start_date = fields.Boolean(string="Editar datos de destino", compute='_compute_is_edit_start_date')
    is_edit_end_date_environment = fields.Boolean(string="Editar datos de origen",
                                                  compute='_compute_is_edit_end_date_environment')
    is_edit_end_date = fields.Boolean(string="Editar datos de origen", compute='_compute_is_edit_end_date')

    _sql_constraints = [
        ('stage_uniq', 'unique(general_cycle_id,operating_unit_id)',
         u'Solo se puede tener una configuración para el año'),
    ]

    @api.depends('end_date')
    def _compute_show_buttons(self):
        for record in self:
            if record.end_date and record.end_date <= fields.Date.today():
                record.show_buttons = True
            else:
                record.show_buttons = False

    @api.depends('start_date')
    def _compute_is_edit_start_date(self):
        for record in self:
            if not record.id or record.end_date <= fields.Date.today():
                record.is_edit_start_date = True
            else:
                record.is_edit_start_date = False

    @api.depends('end_date_environment')
    def _compute_is_edit_end_date_environment(self):
        for record in self:
            if not record.id or record.end_date_environment <= fields.Date.today():
                record.is_edit_end_date_environment = True
            else:
                record.is_edit_end_date_environment = False

    @api.depends('end_date')
    def _compute_is_edit_end_date(self):
        for record in self:
            if not record.id or record.end_date <= fields.Date.today():
                record.is_edit_end_date = True
            else:
                record.is_edit_end_date = False

    @api.constrains("start_date", "end_date", "end_date_environment")
    def _check_date(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.start_date > record.general_cycle_id.start_date_max:
                raise ValidationError(
                    _(u"La fecha inicio debe ser menor o igual a la fecha de inicio máxima del ciclo general"))
            if record.start_date < record.general_cycle_id.start_date:
                raise ValidationError(
                    _(u"La fecha inicio debe ser mayor o igual a la fecha de inicio del ciclo general"))
            if record.end_date > record.general_cycle_id.end_date_max:
                raise ValidationError(
                    _(u"La fecha fin debe ser menor o igual a la fecha de fin máxima del ciclo general"))
            if record.end_date_environment > record.end_date:
                raise ValidationError(
                    _(u"La Fecha fin def. entorno debe ser menor o igual a la fecha de fin máxima del ciclo general"))

    def action_extend_deadline(self):
        return True

    def action_close_stage(self):
        return True

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['year'] = _("%s (Copia)") % self.year
        return super(ONSCDesempenoEvaluationStage, self).copy(default=default)

    def write(self, vals):
        if vals.get('start_date') and datetime.datetime.strptime(vals.get('start_date'), '%Y-%m-%d').date() > fields.Date.today():
            raise ValidationError(_("La fecha inicio debe ser mayor a la fecha actual"))
        return super(ONSCDesempenoEvaluationStage, self).write(vals)

    @api.model
    def create(self, vals):
        if datetime.datetime.strptime(vals.get('start_date'), '%Y-%m-%d').date() > fields.Date.today():
            raise ValidationError(_("La fecha inicio debe ser mayor a la fecha actual"))
        return super(ONSCDesempenoEvaluationStage, self).create(vals)
