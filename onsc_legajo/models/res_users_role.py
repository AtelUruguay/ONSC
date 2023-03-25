# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsersRole(models.Model):
    _inherit = "res.users.role"

    is_byinciso = fields.Boolean(string='Habilitado por inciso')
