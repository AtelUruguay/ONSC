# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDocketDocumentType(models.Model):
    _name = 'onsc.docket.document.type'
    _description = 'Tipo de documento'

    name = fields.Char("Nombre del tipo de documento", required=True)
    description = fields.Char(u"Descripción", required=True)
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del tipo de documento debe ser único'),
    ]
