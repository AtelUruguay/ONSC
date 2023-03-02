# -*- coding: utf-8 -*-
import json

from odoo import fields, models


class ONSCLegajoSecurityJob(models.Model):
    _name = 'onsc.legajo.security.job'
    _description = 'Seguridad de puesto'

    name = fields.Char(string='Nombre de la seguridad de puesto', required=True)
    is_uo_manager = fields.Boolean(string='Es responsable UO')
    user_role_ids = fields.Many2many('res.users.role', string='Roles', required=True)
    active = fields.Boolean('Activo', default=True)
    user_role_ids_domain = fields.Char(default=lambda self: self._user_role_is_domain(),
                                       compute='_compute_user_role_ids_domain')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la seguridad de puesto debe ser única'),
    ]

    def _compute_user_role_ids_domain(self):
        for rec in self:
            rec.user_role_ids_domain = self._user_role_id_domain()

    def _user_role_ids_domain(self):
        return json.dumps([('id', 'in', self.env.ref('base.default_user').role_line_ids.mapped('role_id').ids)])
