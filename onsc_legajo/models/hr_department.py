# -*- coding: utf-8 -*-

from odoo import fields, models


class Department(models.Model):
    _name = "hr.department"

    is_manager_reserved = fields.Boolean(string='¿Está el responsable reservado?')
