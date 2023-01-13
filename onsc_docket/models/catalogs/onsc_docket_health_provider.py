# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDocketHealthProvider(models.Model):
    _name = 'onsc.docket.health.provider'
    _description = 'Prestadores de salud'

    code = fields.Char(u"Código", required=True)
    name = fields.Char("Nombre del prestador de salud", required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código del prestador de salud debe ser único'),
        ('name_uniq', 'unique(name)', u'El nombre del prestador de salud debe ser único'),
    ]
