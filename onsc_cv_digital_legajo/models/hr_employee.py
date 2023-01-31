# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.cv.common.data']

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_cv_digital_id',
                                    store=True)
    drivers_license_ids = fields.One2many("onsc.legajo.driver.license",
                                          inverse_name="legajo_id",
                                          string="Licencias de conducir",
                                          copy=True)

    # RAZA
    cv_race_ids = fields.Many2many("onsc.cv.race", string=u"Identidad étnico-racial",
                                   domain="[('race_type','in',['race','both'])]")
    is_cv_race_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        compute='_compute_cv_race_values', store=True)
    is_multiple_cv_race_selected = fields.Boolean(
        u'Múltiples razas seleccionadas',
        compute='_compute_cv_race_values', store=True)
    cv_first_race_id = fields.Many2one("onsc.cv.race", string=u"¿Con cuál se reconoce principalmente?",
                                       domain="[('id','in',cv_race_ids)]")

    @api.depends('cv_emissor_country_id', 'cv_document_type_id', 'cv_nro_doc')
    def _compute_cv_digital_id(self):
        CVDigital = self.env['onsc.cv.digital']
        for record in self:
            self.cv_digital_id = CVDigital.search([
                ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                ('cv_document_type_id', '=', record.cv_document_type_id.id),
                ('cv_nro_doc', '=', record.cv_nro_doc),
            ], limit=1)

    @api.depends('cv_race_ids')
    def _compute_cv_race_values(self):
        for record in self:
            record.is_cv_race_option_other_enable = len(
                record.cv_race_ids.filtered(lambda x: x.is_option_other_enable)) > 0
            record.is_multiple_cv_race_selected = len(record.cv_race_ids) > 1

    def _get_driver_licences_orm(self):
        driver_licences_orm = [(5,)]
        for drivers_license in self.cv_digital_id.drivers_license_ids:
            driver_licences_orm.append((0, 0, {
                'validation_date': drivers_license.validation_date,
                'category_id': drivers_license.category_id.id,
                'license_file': drivers_license.license_file,
                'license_filename': drivers_license.license_filename,
            }))
        return driver_licences_orm

    def button_get_info_fromcv(self):
        for record in self.suspend_security():
            vals = {
                'cv_first_name': record.cv_digital_id.partner_id.cv_first_name,
                'cv_second_name': record.cv_digital_id.partner_id.cv_second_name,
                'cv_last_name_1': record.cv_digital_id.partner_id.cv_last_name_1,
                'cv_last_name_2': record.cv_digital_id.partner_id.cv_last_name_2,
                'photo_updated_date': record.cv_digital_id.partner_id.cv_photo_updated_date,
                'cv_birthdate': record.cv_digital_id.partner_id.cv_birthdate,
                'document_identity_file': record.cv_digital_id.document_identity_file,
                'document_identity_filename': record.cv_digital_id.document_identity_filename,
                'cv_sex': record.cv_digital_id.cv_sex,
                'cv_sex_updated_date': record.cv_digital_id.cv_sex_updated_date,
                # Datos personales
                'country_of_birth_id': record.cv_digital_id.country_of_birth_id.id,
                'marital_status_id': record.cv_digital_id.marital_status_id.id,
                'uy_citizenship': record.cv_digital_id.uy_citizenship,
                'crendencial_serie': record.cv_digital_id.crendencial_serie,
                'credential_number': record.cv_digital_id.credential_number,
                'civical_credential_file': record.cv_digital_id.civical_credential_file,
                'civical_credential_filename': record.cv_digital_id.civical_credential_filename,
                'prefix_phone_id': record.cv_digital_id.prefix_phone_id.id,
                'personal_phone': record.cv_digital_id.personal_phone,
                'prefix_mobile_phone_id': record.cv_digital_id.prefix_mobile_phone_id.id,
                'mobile_phone': record.cv_digital_id.mobile_phone,
                'email': record.cv_digital_id.email,
                'cjppu_affiliate_number': record.cv_digital_id.cjppu_affiliate_number,
                'professional_resume': record.cv_digital_id.professional_resume,
                'user_linkedIn': record.cv_digital_id.user_linkedIn,
                'is_driver_license': record.cv_digital_id.is_driver_license,
                # 'drivers_license_ids': record._get_driver_licences_orm()
                # GENERO
                'cv_gender_id': record.cv_digital_id.cv_gender_id.id,
                'cv_gender2': record.cv_digital_id.cv_gender2,
                'cv_gender_record_file': record.cv_digital_id.cv_gender_record_file,
                'cv_gender_record_filename': record.cv_digital_id.cv_gender_record_filename,
                'is_cv_gender_public': record.cv_digital_id.is_cv_gender_public,
                # RAZA
                'cv_race2': record.cv_digital_id.cv_race2,
            }
            record.write(vals)


class ONSCLegajoDriverLicense(models.Model):
    _name = 'onsc.legajo.driver.license'
    _description = 'Licencia de conducir'

    legajo_id = fields.Many2one("onsc.legajo", string="Legajo", required=True, index=True, ondelete='cascade')
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    license_file = fields.Binary("Documento digitalizado licencia de conducir")
    license_filename = fields.Char('Nombre del documento digital')

    @api.model
    def create(self, values):
        record = super(ONSCLegajoDriverLicense, self).create(values)
        return record
