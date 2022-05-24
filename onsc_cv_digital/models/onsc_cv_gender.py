# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVGender(models.Model):
    _name = 'onsc.cv.gender'
    _description = 'Género'

    # _rec_name = 'name'
    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre del género', required=True)
    active = fields.Boolean(string='Activo', default=True)
    is_option_other_enable = fields.Boolean(u'¿Permitir opción Otra/o ?')


    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre del género debe ser único'),
    ]
    
