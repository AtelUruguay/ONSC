# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDocketStateSquare(models.Model):
    _name = 'onsc.docket.state.square'
    _description = 'Estado de la plaza'

    name = fields.Char(string='Descripción', required=True)
    code = fields.Char(string='Código', required=True)
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código del estado de la plaza debe ser único'),
        ('name_uniq', 'unique(name)', u'La descripción del estado de la plaza debe ser única'),
    ]
