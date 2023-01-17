# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDocketJobType(models.Model):
    _name = 'onsc.docket.job.type'
    _description = 'Tipo de Puesto'

    name = fields.Char(string='Nombre del tipo de puesto', required=True)
    is_uo_responsible = fields.Boolean(string='Es responsable UO')
    role_ids = fields.Many2many('res.groups', string='Roles')
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del tipo del puesto debe ser único'),
    ]
