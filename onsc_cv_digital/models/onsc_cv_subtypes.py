# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVSubtypePublication(models.Model):
    _name = 'onsc.cv.subtype.publication'
    _description = 'Sub tipo de publicación'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del sub tipo de publicación', required=True)
    active = fields.Boolean(string="Activo", default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del sub tipo de publicación debe ser único')
    ]


class ONSCCVSubtypeProduction(models.Model):
    _name = 'onsc.cv.subtype.production'
    _description = 'Sub tipo de producción'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del sub tipo de producción', required=True)
    active = fields.Boolean(string="Activo", default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del sub tipo de producción debe ser único')
    ]


class ONSCCVSubtypeEvaluation(models.Model):
    _name = 'onsc.cv.subtype.evaluation'
    _description = 'Sub tipo de evaluación'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del sub tipo de evaluación', required=True)
    active = fields.Boolean(string="Activo", default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del sub tipo de evaluación debe ser único')
    ]


class ONSCCVSubtypeOther(models.Model):
    _name = 'onsc.cv.subtype.other'
    _description = 'Sub tipo otro'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del sub tipo otro', required=True)
    active = fields.Boolean(string="Activo", default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción otra/o?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del sub tipo otro debe ser único')
    ]
