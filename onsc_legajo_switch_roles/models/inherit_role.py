# -*- coding: utf-8 -*-
import logging

from odoo import SUPERUSER_ID, api, fields, models


class ResUsersRole(models.Model):
    _inherit = "res.users.role"

    rol_type = fields.Selection(
        [
            ('default', 'Rol por defecto'),
            ('adding_job', 'Rol de adición de puesto'),
        ],
        string="Tipo de Rol"
    )
