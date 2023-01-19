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
        ('code_error_uniq', 'unique(code_error)', u'El código del error de integración debe ser único'),
        ('integration_code_uniq', 'unique(integration_code)', u'El código de integración debe ser única'),
    ]
