# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsersRole(models.Model):
    _inherit = "res.users.role.line"

    is_job_role_line = fields.Boolean('Es un rol de puestos')
