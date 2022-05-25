# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDocumentType(models.Model):
    _name = 'onsc.cv.document.type'
    _description = 'Tipo de Documento'

    code = fields.Char(string=u"Código")
    name = fields.Char(string=u"Nombre del Tipo de documento", required=True)
    active = fields.Boolean(string="Activo", default=True)
    code_other = fields.Char(string=u"Otro código")
    is_org = fields.Boolean(u'Aplica organismo')
    is_sice = fields.Boolean(u'Aplica SICE')
    code_sice = fields.Char(u'Código SICE')
    is_rupe = fields.Boolean(u'Aplica RUPE')
    code_rupe = fields.Char(u'Código RUPE')
    is_dgi = fields.Boolean(u'Aplica DGI')
    code_dgi = fields.Char(u'Código DGI')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Tipo de Documento debe ser único'),
    ]
