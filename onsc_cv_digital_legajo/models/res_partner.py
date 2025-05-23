# -*- coding: utf-8 -*-
import logging

from email_validator import validate_email

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

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
        new_args = []
        for args_item in args:
            if (isinstance(args_item, tuple) or isinstance(args_item, list)) and args_item[0] == 'name' and len(
                    args_item) == 3:
                new_args.append('|')
                new_args.append(args_item)
                new_args.append(('cv_nro_doc', args_item[1], args_item[2]))
            else:
                new_args.append(args_item)
        return super(ResPartner, self)._search(new_args, offset=offset, limit=limit, order=order, count=count,
                                               access_rights_uid=access_rights_uid)

    address_info_date = fields.Date(string="Fecha de información domicilio")
    address_receipt_file = fields.Binary('Documento digitalizado "Constancia de domicilio"')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')

    institutional_email = fields.Char(string=u'Correo electrónico institucional',
                                      compute='_compute_institutional_email')

    def _compute_institutional_email(self):
        """
        SI TIENE CV SE TOMA EL MAIL INSTITUCIONAL DEL CV
        """
        CVDigital = self.env['onsc.cv.digital'].sudo()
        for record in self:
            cv_digital = CVDigital.search([('partner_id', '=', record.id), ('type', '=', 'cv')],
                                          limit=1)
            if cv_digital.institutional_email:
                record.institutional_email = cv_digital.institutional_email
            else:
                record.institutional_email = record.email

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

    def get_onsc_mails(self):
        CVDigital = self.env['onsc.cv.digital'].sudo()
        followers_emails = []
        for follower in self:
            try:
                cv_digital = CVDigital.search([('partner_id', '=', follower.id), ('type', '=', 'cv')],
                                              limit=1)
                if cv_digital.institutional_email:
                    partner_email = cv_digital.institutional_email
                else:
                    partner_email = follower.email
                validate_email(partner_email)
                followers_emails.append(partner_email)
            except Exception:
                # Si el email no es válido, se captura la excepción
                _logger.info(_("Mail de Contacto no válido: %s") % follower.email)
        return ','.join(followers_emails) or ''
