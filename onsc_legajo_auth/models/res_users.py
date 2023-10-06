# -*- coding: utf-8 -*-

from odoo import models, api


class ResUsers(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        user_id = super(ResUsers, self).create(values)
        user_id._update_employee_user()
        return user_id

    def _update_employee_user(self, values):
        employee = self.env['hr.employee'].sudo().search([
            ('cv_emissor_country_id', '=', self.cv_emissor_country_id.id),
            ('cv_document_type_id', '=', self.cv_document_type_id.id),
            ('cv_nro_doc', '=', self.cv_nro_doc),
            ('user_id', '=', False)
        ], limit=1)
        if employee:
            employee.suspend_security().write({
                'user_id': self.id,
            })
        return True
