# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDriversLicenseCategories(models.Model):
    _name = 'onsc.cv.drivers.license.categories'
    _description = 'Categoría de Licencia de conducir'

    code = fields.Char(string=u"Código")
    name = fields.Char(string='Nombre de la Categoría de licencia de conducir', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la Categoría de Licencia de conducir debe ser único'),
    ]
