# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api, _

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class HrJob(models.Model):
    _inherit = 'hr.job'

    start_date = fields.Date(string="Fecha desde", default=fields.Date.today())
    end_date = fields.Date(string="Fecha hasta")
    role_ids = fields.One2many('hr.job.role.line', inverse_name='job_id', string="Roles", tracking=True,
                               domain=[('type', '=', 'system')], )
    role_extra_ids = fields.One2many('hr.job.role.line', inverse_name='job_id', string="Roles adicionales",
                                     tracking=True, domain=[('type', '=', 'manual')])
    active = fields.Boolean('Activo', default=True)
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto", ondelete='restrict')
    contract_id = fields.Many2one('hr.contract', string="Contrato", ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', string="Empleado", ondelete='restrict')
    is_readonly = fields.Boolean(string="Solo lectura", compute="_compute_is_readonly")
    department_id_domain = fields.Char(compute='_compute_department_domain')

    @api.depends('contract_id')
    def _compute_department_domain(self):
        for rec in self:
            if rec.contract_id:
                rec.department_id_domain = json.dumps([('id', '=', rec.contract_id.department_id.id)])
            else:
                rec.department_id_domain = json.dumps([])

    def _compute_is_readonly(self):
        for record in self:
            record.is_readonly = not self.user_has_groups('onsc_legajo.group_legajo_configurador_puesto')

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde"))

    @api.onchange('security_job_id')
    def onchange_security_job_id(self):
        if self.security_job_id:
            _role_ids = [(5, 0)]
            _role_ids.extend([
                (0, 0,
                 {'user_role_id': role.id, 'type': 'system',
                  'start_date': self.start_date if self.start_date else fields.Date.today()})
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
    _name = 'hr.job.role.line'
    _description = 'Línea de roles de puesto'

    job_id = fields.Many2one('hr.job', string='Puesto', ondelete='cascade')
    user_role_id = fields.Many2one('res.users.role', string='Rol', required=True, ondelete='restrict')
    start_date = fields.Date(string="Fecha desde")
    end_date = fields.Date(string="Fecha hasta")
    type = fields.Selection([('manual', 'Manual'), ('system', 'Seguridad de puesto')],
                            string='Modo de creación', default='manual')

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
