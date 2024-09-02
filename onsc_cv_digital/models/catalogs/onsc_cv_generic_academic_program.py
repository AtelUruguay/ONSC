# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVGenericAcademicProgram(models.Model):
    _name = 'onsc.cv.generic.academic.program'
    _description = 'Programas académicos genérico'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del programa académico', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del programa académico debe ser único'), ]
