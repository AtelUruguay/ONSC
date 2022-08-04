# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVStatusCivil(models.Model):
    _name = 'onsc.catalog.hierarchical.level'
    _description = 'Nivel jerárquico'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del nivel jerárquico', required=True)
    description = fields.Text(string='Descripción')
    order = fields.Integer(string="Orden")
    is_central_admin = fields.Boolean(string="¿Es administración central?")

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del nivel jerárquico debe ser único'),
    ]
