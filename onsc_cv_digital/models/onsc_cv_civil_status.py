# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVStatusCivil(models.Model):
    _name = 'onsc.cv.status.civil'
    _description = 'Estado Civil'

    code = fields.Char(string=u"Código de identificación")
    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre debe ser único!'),
    ]
