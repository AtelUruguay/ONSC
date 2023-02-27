# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api, fields, models


class ResUsersRole(models.Model):
    _inherit = "res.users.role"

    rol_type = fields.Selection(
        [
            ('default', 'Rol por defecto'),
            ('config_onsc', 'Rol de configurador ONSC'),
        ],
        string="Tipo de Rol"
    )
