# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDocketEmergency(models.Model):
    _name = 'onsc.docket.emergency'
    _description = 'Emergencia'

    code = fields.Char(u"Código", required=True)
    name = fields.Char("Nombre de la emergencia", required=True)
    phone = fields.Char(u"Teléfono")

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código de la emergencia debe ser único'),
        ('name_uniq', 'unique(name)', u'El nombre de la emergencia debe ser único'),
    ]
