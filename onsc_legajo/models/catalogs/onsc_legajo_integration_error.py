# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import fields, models, _


class ONSCLegajoIntegrationError(models.Model):
    _name = 'onsc.legajo.integration.error'
    _description = 'Error de integración'
    _rec_name = 'integration_code'

    integration_code = fields.Char(string='Código de integración', required=True)
    code_error = fields.Char(string='Código de error', required=True)
    description = fields.Char(string='Descripción', required=True)
    is_system_required = fields.Boolean('Requeridos por el sistema', default=False)
    active = fields.Boolean('Activo', default=True)

    _sql_constraints = [
        ('integration_code_uniq', 'unique(integration_code,code_error)', u'El código de error debe ser único por integración')
    ]

    def unlink(self):
        if self.filtered(lambda x:x.is_system_required):
            raise ValidationError(_("No se pueden eliminar códigos de integración imprescindibles "
                                    "para el correcto funcionamiento del sistema"))
        return super(ONSCLegajoIntegrationError, self).unlink()
