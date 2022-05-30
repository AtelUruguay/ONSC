# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVStatusCivil(models.Model):
    _name = 'onsc.cv.status.civil'
    _description = 'Estado Civil'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre del Estado Civil', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Estado Civil debe ser único'),
    ]


class ONSCCVDriversLicenseCategories(models.Model):
    _name = 'onsc.cv.drivers.license.categories'
    _description = 'Categoría de Licencia de conducir'
    _order = 'name'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre de la Categoría de licencia de conducir', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la Categoría de Licencia de conducir debe ser único'),
    ]


class ONSCCVGender(models.Model):
    _name = 'onsc.cv.gender'
    _description = 'Género'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del Género', required=True)
    active = fields.Boolean(string='Activo', default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción Otra/o ?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Género debe ser único'),
    ]


class ONSCCVRace(models.Model):
    _name = 'onsc.cv.race'
    _description = 'Raza'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la Raza', required=True)
    active = fields.Boolean(string='Activo', default=True)
    race_type = fields.Selection(
        string=u'Tipo',
        selection=[('race', u'Raza'),
                   ('recognition', u'Reconocimiento'),
                   ('both', u'Ambos')])
    is_option_other_enable = fields.Boolean(u'¿Permitir opción Otra/o ?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la Raza debe ser único'),
    ]


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


class ONSCCVStudyLevel(models.Model):
    _name = 'onsc.cv.study.level'
    _description = 'Nivel de Estudio'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del nivel de estudio', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del Nivel de Estudio debe ser único'),
    ]


class ONSCCVEducationalAreas(models.Model):
    _name = 'onsc.cv.educational.areas'
    _description = 'Areas Educativas'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del área educativa', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El Nombre del Área Educativa debe ser único'),
    ]
