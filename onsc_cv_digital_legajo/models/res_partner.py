# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression

MODIFIED_FIELDS_TO_NOTIFY_SGH = [
    'name',
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_first_name',
    'cv_second_name',
    'cv_birthdate',
    'cv_sex',
    'email'
]

MODIFIED_FIELDS = [
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_first_name',
    'cv_second_name',
    'cv_birthdate',
    'cv_sex',
    'email',
    'cv_sex_updated_date',

    'prefix_phone_id',
    'prefix_mobile_phone_id',
]

MODIFIED_FIELDS_WITH_TRANSFORMATION = {
    'phone': 'personal_phone',
    'mobile': 'mobile_phone',
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        cv_nro_doc_args = []
        for args_item in args:
            if args_item[0] == 'name' and len(args_item) == 3:
                cv_nro_doc_args = [('cv_nro_doc', args_item[1], args_item[2])]

        if len(cv_nro_doc_args) > 0:
            args = expression.OR([cv_nro_doc_args, args])
        return super(ResPartner, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)

    address_info_date = fields.Date(string="Fecha de información domicilio")
    address_receipt_file = fields.Binary('Documento digitalizado "Constancia de domicilio"')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')

    def _check_entities_values_before_write(self, values):
        self.suspend_security()._update_employee_status(values)
        return super(ResPartner, self)._check_entities_values_before_write(values)

    def _update_employee_status(self, values):
        BaseUtils = self.env['onsc.base.utils'].sudo()
        employees = self.env['hr.employee']
        valid_cvs = self.env['onsc.cv.digital'].search([
            ('type', '=', 'cv'),
            ('is_docket_active', '=', True),
            ('employee_id', '!=', False),
            ('partner_id', 'in', self.ids)])
        for cv in valid_cvs:
            employee_values_to_write = {}
            values_filtered = BaseUtils.get_really_values_changed(cv.partner_id, values)
            for modified_field in MODIFIED_FIELDS_TO_NOTIFY_SGH:
                if modified_field in values_filtered:
                    employees |= cv.employee_id
            for key, value in values_filtered.items():
                if key in MODIFIED_FIELDS:
                    employee_values_to_write[key] = value
                if key in MODIFIED_FIELDS_WITH_TRANSFORMATION.keys():
                    employee_values_to_write[MODIFIED_FIELDS_WITH_TRANSFORMATION.get(key)] = value
            if len(employee_values_to_write.keys()):
                cv.employee_id.suspend_security().write(employee_values_to_write)
        employees.suspend_security().write({'notify_sgh': True})
