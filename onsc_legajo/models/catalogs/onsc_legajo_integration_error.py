# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoIntegrationError(models.Model):
    _name = 'onsc.legajo.integration.error'
    _description = 'Error de integración'
    _rec_name = 'integration_code'

    integration_code = fields.Char(string='Código de integración', required=True)
    code_error = fields.Char(string='Código de error', required=True)
    description = fields.Char(string='Descripción', required=True)
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('integration_code_uniq', 'unique(integration_code,code_error)', u'El código de error debe ser único por integración')
    ]
