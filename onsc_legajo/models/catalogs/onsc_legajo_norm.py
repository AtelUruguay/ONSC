# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoNorm(models.Model):
    _name = 'onsc.legajo.norm'
    _description = 'Norma'
    _rec_name = 'pk'

    pk = fields.Char(string=u"Código", required=True)
    anioNorma = fields.Integer(string=u"Año")
    numeroNorma = fields.Integer(string=u"Número")
    articuloNorma = fields.Integer(string=u"Artículo")
    numeroLiteral = fields.Char(string="Número literal")
    tipoNormaSigla = fields.Char(string="Tipo norma sigla")
    tipoNorma = fields.Char(string="Tipo norma")
    descripcion = fields.Char(string=u"Descripción")
    fechaDerogacion = fields.Date(string=u"Fecha derogación")
    fechaVencimiento = fields.Date(string="Fecha vencimiento")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('pk_uniq', 'unique(pk)', u'El código de la norma debe ser único')
    ]

    def syncronize(self):
        return True
