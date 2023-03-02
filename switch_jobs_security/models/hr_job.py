# -*- coding: utf-8 -*-

from odoo import fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    start_date = fields.Date(string="Fecha desde", default=fields.Date.today())
    end_date = fields.Date(string="Fecha hasta")
    role_ids = fields.One2many('hr.job.role.line', inverse_name='job_id', string="Roles", tracking=True,
                               domain=[('type', '=', 'system')], )
    role_extra_ids = fields.One2many('hr.job.role.line', inverse_name='job_id', string="Roles adicionales",
                                     tracking=True, domain=[('type', '=', 'manual')])
    active = fields.Boolean('Activo', default=True)
    contract_id = fields.Many2one('hr.contract', string="Contrato", ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', string="Empleado", ondelete='restrict')


class HrJobRoleLine(models.Model):
    _name = 'hr.job.role.line'
    _description = 'Línea de roles de puesto'

    job_id = fields.Many2one('hr.job', string='Puesto', ondelete='cascade')
    user_role_id = fields.Many2one('res.users.role', string='Rol', required=True, ondelete='restrict')
    start_date = fields.Date(string="Fecha desde")
    end_date = fields.Date(string="Fecha hasta")
    type = fields.Selection([('manual', 'Manual'), ('system', 'Seguridad de puesto')],
                            string='Modo de creación', default='manual')
