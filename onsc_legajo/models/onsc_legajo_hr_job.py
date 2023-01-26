# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class HrJob(models.Model):
    _inherit = 'hr.job'

    start_date = fields.Date(string="Fecha desde")
    end_date = fields.Date(string="Fecha hasta")
    role_ids = fields.One2many('hr.job.role.line', inverse_name='job_id', string="Roles", tracking=True)
    active = fields.Boolean('Activo', default=True)
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de Puesto", ondelete='restrict')
    hr_contract_id = fields.Many2one('hr.contract', string="Contrato", ondelete='restrict')
    hr_employee_id = fields.Many2one('hr.employee', string="Empleado", ondelete='restrict')
    is_read_only = fields.Boolean(string="Solo lectura", compute="_compute_is_read_only")

    def _compute_is_read_only(self):
        for record in self:
            record.is_read_only = self.user_has_groups(
                'onsc_legajo.group_legajo_configurador_puesto_ajuste_seguridad_manual_inciso') or self.user_has_groups(
                'onsc_legajo.group_legajo_configurador_puesto_ajuste_seguridad_manual_informatica_onsc')

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
            self.role_ids = [(2, role.id) for role in
                             self.role_ids.filtered(lambda r: r.creation_mode == 'seguridad_puesto')]
            self.role_ids = [
                (0, 0, {'user_role_id': role.id, 'creation_mode': 'seguridad_puesto',
                        'start_date': self.start_date if self.start_date else fields.Date.today()})
                for role in
                self.security_job_id.user_role_ids]
        else:
            self.role_ids = [(5, 0, 0)]


class HrJobRoleLine(models.Model):
    _name = 'hr.job.role.line'
    _description = 'Línea de roles de puesto'

    job_id = fields.Many2one('hr.job', string='Puesto', ondelete='cascade')
    user_role_id = fields.Many2one('res.users.role', string='Rol', required=True, ondelete='cascade')
    start_date = fields.Date(string="Fecha desde")
    end_date = fields.Date(string="Fecha hasta")
    creation_mode = fields.Selection([('manual', 'Manual'), ('seguridad_puesto', 'Seguridad de Puesto')],
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



