# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ONSCCVRace(models.Model):
    _name = 'onsc.cv.race'
    _description = 'Raza'

    code = fields.Char(u'Código')
    name = fields.Char(u'Nombre de la raza', required=True)
    active = fields.Boolean(string='Activo', default=True)
    race_type = fields.Selection(
        string=u'Tipo',
        selection=[('race', u'Raza'),
                   ('recognition', u'Reconocimiento'),
                   ('both', u'Ambos'),],
        required=False, )
    is_option_other_enable = fields.Boolean(u'¿Permitir opción Otra/o ?')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         u'El nombre de la raza debe ser único'),
    ]
    
