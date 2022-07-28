# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from .onsc_cv_useful_tools import is_valid_email
from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning
from .onsc_cv_useful_tools import is_valid_phone

REFERENCE_TYPES = [('staff', 'Personal'), ('working', 'Laboral')]


class ONSCCVDigitalReference(models.Model):
    _name = 'onsc.cv.reference'
    _description = 'Referencias'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", required=True, index=True, ondelete='cascade')
    reference_type = fields.Selection(REFERENCE_TYPES, 'Tipo de referencia', required=True)
    name = fields.Char('Nombre', required=True)
    phone = fields.Char('Teléfono')
    email = fields.Char('Mail')
    company_name = fields.Char('Empresa')
    notes = fields.Text('Comentarios adicionales')
    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]))

    @api.onchange('email')
    def onchange_email(self):
        if self.email and not is_valid_email(self.email):
            self.email = False
            return cv_warning(_('El mail ingresado no tiene un formato válido'))

    @api.onchange('phone', 'prefix_phone_id')
    def onchange_phone(self):
        phone_formatted, format_with_error, invalid_phone = is_valid_phone(self.phone, self.prefix_phone_id.country_id)
        self.phone = phone_formatted
        if format_with_error:
            return cv_warning(_("El teléfono ingresado no es válido"))
        if invalid_phone:
            return cv_warning(
                _("El teléfono ingresado no es válido para %s" % self.prefix_phone_id.country_id.name))
