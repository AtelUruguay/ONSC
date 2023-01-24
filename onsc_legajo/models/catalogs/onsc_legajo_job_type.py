# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoJobType(models.Model):
    _name = 'onsc.legajo.job.type'
    _description = 'Tipo de Puesto'

    name = fields.Char(string='Nombre del tipo de puesto', required=True)
    is_uo_manager = fields.Boolean(string='Es responsable UO')
    user_role_ids = fields.Many2many('res.users.role', string='Roles', required=True)
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del tipo del puesto debe ser único'),
    ]
