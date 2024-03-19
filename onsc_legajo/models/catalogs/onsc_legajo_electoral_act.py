# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoElectoralAct(models.Model):
    _name = 'onsc.legajo.electoral.act'
    _description = "Rol acto electoral"

    name = fields.Char(string="Nombre")
    act_date = fields.Date(string="Fecha del Acto")
    holiday_date = fields.Date(string="Fecha del asueto")
    active = fields.Boolean(string='Activo')
    required = fields.Boolean('Obligatorio')
    date_since_entry_control = fields.Date('Fecha desde ingreso control')
    date_until_entry_control = fields.Date('Fecha hasta ingreso control')
    date_since_consultation_control = fields.Date('Fecha desde consulta control')
    date_until_consultation_control = fields.Date('Fecha hasta consulta control')
    type_responsability_ids = fields.One2many(comodel_name="onsc.legajo.electoral.act.type.responsability",
                                              inverse_name="electoral_act_id",
                                              string="Tipo Responsabilidad")

    _sql_constraints = [('name_uniq', 'UNIQUE (name)', _('Ya existe una acto electoral con el mismo nombre'))]

    @api.constrains("date_since_entry_control", "date_until_entry_control", "date_since_consultation_control",
                    "date_until_consultation_control")
    def _check_date_range(self):
        for record in self:
            if record.date_since_entry_control and record.date_until_entry_control and \
                    record.date_since_entry_control > record.date_until_entry_control:
                raise ValidationError(_("La fecha desde de ingreso debe ser menor a la fecha hasta de ingreso"))
            if record.date_since_consultation_control and record.date_until_consultation_control and \
                    record.date_since_consultation_control > record.date_until_consultation_control:
                raise ValidationError(_("La fecha desde de consulta debe ser menor a la fecha hasta de ingreso"))
            if record.date_since_entry_control and record.date_since_consultation_control and \
                    record.date_since_entry_control < record.date_since_consultation_control:
                raise ValidationError(_("La fecha desde de ingreso está fuera del rango de fechas de consulta"))
            if record.date_until_entry_control and record.date_until_consultation_control and record.date_until_entry_control > record.date_until_consultation_control:
                raise ValidationError(_("La fecha hasta está fuera del rango de fechas de consulta"))

    @api.onchange('required')
    def _onchange_required(self):
        if not self.required:
            self.date_since_consultation_control = False
            self.date_until_consultation_control = False
            self.date_since_entry_control = False
            self.date_until_entry_control = False


class ONSCLegajoRoleElectoralAct(models.Model):
    _name = 'onsc.legajo.role.electoral.act'
    _description = "Rol acto electoral"

    _sql_constraints = [
        ('code_unique', 'unique(code)', _(u'Ya existe un rol con ese código')),
        ('name_unique', 'unique(name)', _('Ya existe un rol con ese nombre'))
    ]

    code = fields.Char(string=u"Código", required=True)
    name = fields.Char(string="Nombre", required=True)
    holiday_work = fields.Boolean(string=u'Corresponde asueto?')
    allow_holidays_work = fields.Boolean(string=u'Permite seleccionar trabajo en asueto?')

    @api.onchange('holiday_work')
    def _onchange_holiday_work(self):
        if not self.holiday_work:
            self.allow_holidays_work = False


class ONSCLegajoElectoralActTypeResponsability(models.Model):
    _name = 'onsc.legajo.electoral.act.type.responsability'
    _rec_name = 'role_id'

    electoral_act_id = fields.Many2one("onsc.legajo.electoral.act", "Acto electoral")
    role_id = fields.Many2one("onsc.legajo.role.electoral.act", " Rol Acto electoral", required=True,
                              ondelete='restrict')
    days = fields.Integer("Días")

    _sql_constraints = [('role_uniq', 'UNIQUE (electoral_act_id,role_id)',
                         _('Ya existe mas de un rol de acto electoral, en el mismo acto electoral'))]
