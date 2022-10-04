# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

from .onsc_cv_useful_tools import is_valid_email

REFERENCE_TYPES = [('staff', 'Personal'), ('working', 'Laboral')]


class ONSCCVDigitalReference(models.Model):
    _name = 'onsc.cv.reference'
    _description = 'Referencias'
    _inherit = ['onsc.cv.abstract.phone.validated', 'onsc.cv.abstract.common']

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'phone')]

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
    phone_full = fields.Char(compute='_compute_phone_full', string='Teléfono')

    @api.depends('prefix_phone_id', 'phone')
    def _compute_phone_full(self):
        for rec in self:
            rec.phone_full = '+%s %s' % (rec.prefix_phone_id.prefix_code, rec.phone)

    @api.onchange('email')
    def onchange_email(self):
        if self.email and not is_valid_email(self.email):
            self.email = False
            return cv_warning(_('El mail ingresado no tiene un formato válido'))

    def _get_json_dict(self):
        return [
            "id",
            'reference_type',
            'name',
            'phone',
            'email',
            'company_name',
            'notes',
            'prefix_phone_id',
            'phone_full',
        ]
