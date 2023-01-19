# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoDocumentType(models.Model):
    _name = 'onsc.legajo.document.type'
    _description = 'Tipo de documento'

    name = fields.Char("Nombre del tipo de documento", required=True)
    description = fields.Char(u"Descripción", required=True)
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del tipo de documento debe ser único'),
    ]
