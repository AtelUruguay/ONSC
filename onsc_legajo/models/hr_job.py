# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response
from odoo.exceptions import ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'

    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto", ondelete='restrict')
    is_readonly = fields.Boolean(string="Solo lectura", compute="_compute_is_readonly")
    department_id_domain = fields.Char(compute='_compute_department_domain')

    @api.constrains("contract_id", "start_date", "end_date")
    def _check_date_range_into_contract(self):
        for record in self:
            if record.start_date < record.contract_id.date_start:
                raise ValidationError(_("La fecha desde está fuera del rango de fechas del contrato"))
            if record.end_date and record.contract_id.date_end and record.end_date > record.contract_id.date_end:
                raise ValidationError(_("La fecha hasta está fuera del rango de fechas del contrato"))

    @api.depends('contract_id')
    def _compute_department_domain(self):
        UOs = self.env['hr.department']
        for rec in self:
            uos = UOs.search([('operating_unit_id', '=', rec.contract_id.operating_unit_id.id)])
            rec.department_id_domain = json.dumps([('id', 'in', uos.ids)])

    def _compute_is_readonly(self):
        for record in self:
            record.is_readonly = not self.user_has_groups('onsc_legajo.group_legajo_configurador_puesto')

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta"))
        self.role_ids.start_date = self.start_date
        self.role_extra_ids.filtered(
            lambda x: x.start_date is False or x.start_date < self.start_date).start_date = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde"))
        self.role_ids.end_date = self.end_date
        if self.end_date:
            self.role_extra_ids.filtered(
                lambda x: x.end_date is False or x.end_date > self.end_date).end_date = self.end_date

    @api.onchange('security_job_id')
    def onchange_security_job_id(self):
        if self.security_job_id:
            _role_ids = [(5, 0)]
            _role_ids.extend([
                (0, 0, {
                    'user_role_id': role.id,
                    'type': 'system',
                    'start_date': self.start_date if self.start_date else fields.Date.today(),
                    'end_date': self.end_date
                })
                for role in
                self.security_job_id.user_role_ids])
            self.role_ids = _role_ids
        else:
            self.role_ids = [(5, 0)]

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = False
        self.department_id = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.department_id = False


class HrJobRoleLine(models.Model):
    _inherit = 'hr.job.role.line'

    user_role_id_domain = fields.Char(default=lambda self: self._user_role_id_domain(),
                                      compute='_compute_user_role_id_domain')

    _sql_constraints = [
        ('recordset_uniq', 'unique(job_id,user_role_id)',
         u'El rol configurado no puede repetirse para el mismo puesto. Revisar la pestaña de Roles y Roles adicionales')
    ]

    @api.constrains("end_date")
    def _check_end_date(self):
        for record in self:
            if record.job_id.end_date and (record.end_date is False or record.end_date > record.job_id.end_date):
                raise ValidationError(
                    _("El periodo de vigencia del rol adicional %s debe estar dentro del periodo de vigencia del puesto") % record.user_role_id.name)

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta"))
        if self.job_id.end_date and self.start_date and self.job_id.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta del puesto"))
        if self.job_id.start_date and self.start_date and self.job_id.start_date > self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser menor que la fecha desde del puesto"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde"))
        if self.job_id.start_date and self.end_date and self.job_id.start_date > self.end_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde del puesto"))
        if self.job_id.end_date and self.end_date and self.job_id.end_date < self.end_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser mayor que la fecha hasta del puesto"))

    def _compute_user_role_id_domain(self):
        for rec in self:
            rec.user_role_id_domain = self._user_role_id_domain()

    def _user_role_id_domain(self):
        if self.user_has_groups(
                'onsc_legajo.group_legajo_configurador_puesto_ajuste_seguridad_manual_informatica_onsc'):
            args = []
        else:
            args = [('is_byinciso', '=', True)]
        roles = self.env['res.users.role'].search(args)
        return json.dumps([('id', 'in', roles.ids)])
