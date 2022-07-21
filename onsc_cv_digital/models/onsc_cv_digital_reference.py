# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from .onsc_cv_useful_tools import is_valid_email
from .onsc_cv_useful_tools import get_onchange_warning_response as cv_warning

REFERENCE_TYPES = [('staff', 'Personal'), ('working', 'Laboral')]


class ONSCCVDigitalReference(models.Model):
    _name = 'onsc.cv.reference'
    _description = 'Referencias'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", required=True, index=True, ondelete='cascade')
    reference_type = fields.Selection(REFERENCE_TYPES, 'Tipo de referencia', required=True)
    name = fields.Char('Nombre', required=True)
    country_id = fields.Many2one('res.country', 'Pais', required=True,
                                 default=lambda self: self.env['res.country'].search([('code', '=', 'UY')]))
    phone = fields.Char('Teléfono')
    phone_full = fields.Char(compute='_compute_phone_full')
    email = fields.Char('Mail')
    company_name = fields.Char('Empresa')
    notes = fields.Text('Comentarios adicionales')

    @api.depends('country_id', 'phone')
    def _compute_phone_full(self):
        for rec in self:
            rec.phone_full = '+%s%s' % (rec.country_id.phone_code, rec.phone)

    @api.onchange('email')
    def onchange_email(self):
        if self.email and not is_valid_email(self.email):
            self.email = False
            return cv_warning(_('El mail ingresado no tiene un formato válido'))

    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone and not self.phone.isdigit():
            return cv_warning(_("El teléfono ingresado no es válido"))

    @api.constrains('phone')
    def check_phone(self):
        for rec in self:
            if rec.phone and not rec.phone.isdigit():
                raise ValidationError(_("El teléfono ingresado no es válido"))
