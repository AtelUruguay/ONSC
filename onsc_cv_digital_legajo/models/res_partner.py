# -*- coding: utf-8 -*-

from odoo import models, fields

MODIFIED_FIELDS = [
    'name',
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_first_name',
    'cv_second_name',
    'cv_birthdate',
    'cv_sex',
    'email'
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    address_info_date = fields.Date(string="Fecha de información domicilio")
    address_receipt_file = fields.Binary('Documento digitalizado "Constancia de domicilio"')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')

    def write(self, vals):
        self.suspend_security()._notify_sgh(vals)
        return super(ResPartner, self).write(vals)

    def _notify_sgh(self, values):
        BaseUtils = self.env['onsc.base.utils'].sudo()
        employees = self.env['hr.employee']
        valid_cvs = self.env['onsc.cv.digital'].search([
            ('type', '=', 'cv'),
            ('is_docket_active', '=', True),
            ('employee_id', '!=', False),
            ('partner_id', 'in', self.ids)])
        for cv in valid_cvs:
            values_filtered = BaseUtils.get_really_values_changed(cv.partner_id, values)
            for modified_field in MODIFIED_FIELDS:
                if modified_field in values_filtered:
                    employees |= cv.employee_id
        employees.suspend_security().write({'notify_sgh': True})
