# -*- coding: utf-8 -*-

from odoo import models, fields


class Department(models.Model):
    _inherit = 'hr.department'

    show_short_name = fields.Boolean(
        'Nombre Corto en Organigrama'
    )
