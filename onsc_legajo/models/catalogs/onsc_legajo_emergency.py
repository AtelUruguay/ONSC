# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCLegajoEmergency(models.Model):
    _name = 'onsc.legajo.emergency'
    _description = 'Emergencia'

    code = fields.Char(u"Código", required=True)
    name = fields.Char("Nombre de la emergencia", required=True)
    phone = fields.Char(u"Teléfono")
    active = fields.Boolean('Activo', default=True)

    @api.model
    def create(self, values):
        if 'code' not in values or ('code' in values and values.get('code') is False):
            values['code'] = self.env['ir.sequence'].next_by_code('onsc.legajo.emergency.code')
        return super(ONSCLegajoEmergency, self).create(values)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código de la emergencia debe ser único'),
        ('name_uniq', 'unique(name)', u'El nombre de la emergencia debe ser único'),
    ]
