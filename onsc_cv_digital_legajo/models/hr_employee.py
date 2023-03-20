# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.cv.common.data', 'onsc.cv.legajo.abstract.common']

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_cv_digital_id',
                                    store=True)
    drivers_license_ids = fields.One2many("onsc.legajo.driver.license",
                                          inverse_name="employee_id",
                                          string="Licencias de conducir",
                                          copy=True, history=True, history_fields="validation_date,category_id")

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

    # Domicilio

    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)',
        groups="hr.group_hr_user,onsc_legajo.group_legajo_configurador_empleado", tracking=True, history=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    cv_address_state_id = fields.Many2one('res.country.state', string='Departamento', history=True)
    cv_address_location_id = fields.Many2one('onsc.cv.location', u'Localidad/Ciudad', history=True)
    cv_address_nro_door = fields.Char(u'Número', history=True)
    cv_address_apto = fields.Char(u'Apto', history=True)
    cv_address_street = fields.Char(u'Calle', history=True)
    cv_address_zip = fields.Char(u'Código postal', history=True)
    cv_address_is_cv_bis = fields.Boolean(u'BIS', history=True)
    cv_address_amplification = fields.Text(u"Aclaraciones")
    cv_address_place = fields.Text(string="Paraje", size=200, history=True)
    cv_address_block = fields.Char(string="Manzana", size=5, history=True)
    cv_address_sandlot = fields.Char(string="Solar", size=5, history=True)
    address_receipt_file = fields.Binary('Documento digitalizado "Constancia de domicilio"')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')

    # Discapacidad
    type_support_ids = fields.Many2many('onsc.cv.type.support', string=u'Tipos de apoyo')
    is_need_other_support = fields.Boolean(u'¿Necesita otro apoyo?')

    # Datos del legajo
    information_contact_ids = fields.One2many('onsc.cv.legajo.information.contact', 'employee_id',
                                              string=u'Información de Contacto', history=True,
                                              history_fields="contact_person_telephone,remark_contact_person")
    last_modification_date = fields.Date(string=u'Fecha última modificación')

    @api.depends('cv_emissor_country_id', 'cv_document_type_id', 'cv_nro_doc')
    def _compute_cv_digital_id(self):
        CVDigital = self.env['onsc.cv.digital']
        for record in self:
            self.cv_digital_id = CVDigital.search([
                ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                ('cv_document_type_id', '=', record.cv_document_type_id.id),
                ('cv_nro_doc', '=', record.cv_nro_doc),
                ('type', '=', 'cv')
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

    def _get_information_contact_orm(self):
        information_contact_orm = [(5,)]
        for information_contact in self.cv_digital_id.information_contact_ids:
            information_contact_orm.append((0, 0, {
                'name_contact': information_contact.name_contact,
                'prefix_phone_id': information_contact.prefix_phone_id.id,
                'contact_person_telephone': information_contact.contact_person_telephone,
                'remark_contact_person': information_contact.remark_contact_person,
            }))
        return information_contact_orm

    def _get_type_support_orm(self):
        type_support_orm = [(5,)]
        for type_support in self.cv_digital_id.type_support_ids:
            type_support_orm.append((4, type_support.id))
        return type_support_orm

    def button_get_info_fromcv(self):
        for record in self:
            record = record.sudo()
            vals = {
                'image_1920': record.cv_digital_id.partner_id.image_1920,
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
                'drivers_license_ids': record._get_driver_licences_orm(),
                'cv_expiration_date': record.cv_digital_id.cv_expiration_date,
                'status_civil_date': record.cv_digital_id.status_civil_date,
                # GENERO
                'cv_gender_id': record.cv_digital_id.cv_gender_id.id,
                'cv_gender2': record.cv_digital_id.cv_gender2,
                'cv_gender_record_file': record.cv_digital_id.cv_gender_record_file,
                'cv_gender_record_filename': record.cv_digital_id.cv_gender_record_filename,
                'is_cv_gender_public': record.cv_digital_id.is_cv_gender_public,
                'gender_date': record.cv_digital_id.gender_date,
                # RAZA
                'cv_race2': record.cv_digital_id.cv_race2,
                'cv_race_ids': record.cv_digital_id.cv_race_ids,
                'cv_first_race_id': record.cv_digital_id.cv_first_race_id,
                'afro_descendants_filename': record.cv_digital_id.afro_descendants_filename,
                'afro_descendants_file': record.cv_digital_id.afro_descendants_file,
                'is_afro_descendants': record.cv_digital_id.is_afro_descendants,
                'is_cv_race_public': record.cv_digital_id.is_cv_race_public,
                'afro_descendant_date': record.cv_digital_id.afro_descendant_date,

                # SALUD LABORAL
                'is_occupational_health_card': record.cv_digital_id.is_occupational_health_card,
                'occupational_health_card_date': record.cv_digital_id.occupational_health_card_date,
                'occupational_health_card_file': record.cv_digital_id.occupational_health_card_file,
                'occupational_health_card_filename': record.cv_digital_id.occupational_health_card_filename,
                # APTITUD MEDICA DEPORTIVA
                'is_medical_aptitude_certificate_status': record.cv_digital_id.is_medical_aptitude_certificate_status,
                'medical_aptitude_certificate_date': record.cv_digital_id.medical_aptitude_certificate_date,
                'medical_aptitude_certificate_file': record.cv_digital_id.medical_aptitude_certificate_file,
                'medical_aptitude_certificate_filename': record.cv_digital_id.medical_aptitude_certificate_filename,
                # Victima de Delitos violentos
                'relationship_victim_violent_file': record.cv_digital_id.relationship_victim_violent_file,
                'is_victim_violent': record.cv_digital_id.is_victim_violent,
                'is_public_information_victim_violent': record.cv_digital_id.is_public_information_victim_violent,
                'relationship_victim_violent_filename': record.cv_digital_id.relationship_victim_violent_filename,
                # Domicilio
                'country_id': record.cv_digital_id.country_id.id,
                'cv_address_street_id': record.cv_digital_id.cv_address_street_id.id,
                'cv_address_street2_id': record.cv_digital_id.cv_address_street2_id.id,
                'cv_address_street3_id': record.cv_digital_id.cv_address_street3_id.id,
                'cv_address_state_id': record.cv_digital_id.cv_address_state_id.id,
                'cv_address_location_id': record.cv_digital_id.cv_address_location_id.id,
                'cv_address_nro_door': record.cv_digital_id.cv_address_nro_door,
                'cv_address_apto': record.cv_digital_id.cv_address_apto,
                'cv_address_street': record.cv_digital_id.cv_address_street,
                'cv_address_zip': record.cv_digital_id.cv_address_zip,
                'cv_address_is_cv_bis': record.cv_digital_id.cv_address_is_cv_bis,
                'cv_address_amplification': record.cv_digital_id.cv_address_amplification,
                'cv_address_place': record.cv_digital_id.cv_address_place,
                'cv_address_block': record.cv_digital_id.cv_address_block,
                'cv_address_sandlot': record.cv_digital_id.cv_address_sandlot,
                'address_receipt_file': record.cv_digital_id.partner_id.address_receipt_file,
                'address_receipt_file_name': record.cv_digital_id.partner_id.address_receipt_file_name,

                # Discapacidad
                'allow_content_public': record.cv_digital_id.allow_content_public,
                'situation_disability': record.cv_digital_id.situation_disability,
                'people_disabilitie': record.cv_digital_id.people_disabilitie,
                'document_certificate_file': record.cv_digital_id.document_certificate_file,
                'document_certificate_filename': record.cv_digital_id.document_certificate_filename,
                'certificate_date': record.cv_digital_id.certificate_date,
                'to_date': record.cv_digital_id.to_date,
                'see': record.cv_digital_id.see,
                'hear': record.cv_digital_id.hear,
                'walk': record.cv_digital_id.walk,
                'speak': record.cv_digital_id.speak,
                'realize': record.cv_digital_id.realize,
                'lear': record.cv_digital_id.lear,
                'interaction': record.cv_digital_id.interaction,
                'is_need_other_support': record.cv_digital_id.is_need_other_support,
                'need_other_support': record.cv_digital_id.need_other_support,
                'disability_date': record.cv_digital_id.disability_date,
                'type_support_ids': record._get_type_support_orm(),
                # Datos del legajo
                'emergency_service_id': record.cv_digital_id.emergency_service_id.id,
                'prefix_emergency_phone_id': record.cv_digital_id.prefix_emergency_phone_id.id,
                'emergency_service_telephone': record.cv_digital_id.emergency_service_telephone,
                'blood_type': record.cv_digital_id.blood_type,
                'other_information_official': record.cv_digital_id.other_information_official,
                'institutional_email': record.cv_digital_id.institutional_email,
                'digitized_document_file': record.cv_digital_id.digitized_document_file,
                'digitized_document_filename': record.cv_digital_id.digitized_document_filename,
                'information_contact_ids': record._get_information_contact_orm(),
                'health_department_id': record.cv_digital_id.health_department_id.id,
                'health_provider_id': record.cv_digital_id.health_provider_id.id,
                # Extras
                'last_modification_date': record.cv_digital_id.last_modification_date,

            }
            record.suspend_security().write(vals)


class ONSCLegajoDriverLicense(models.Model):
    _name = 'onsc.legajo.driver.license'
    _description = 'Licencia de conducir'

    employee_id = fields.Many2one("hr.employee", string="Legajo", required=True, index=True, ondelete='cascade')
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    license_file = fields.Binary("Documento digitalizado licencia de conducir")
    license_filename = fields.Char('Nombre del documento digital')


class ONSCCVLegajoInformationContact(models.Model):
    _name = 'onsc.cv.legajo.information.contact'
    _description = 'Información de Contacto para el legajo'
    _inherit = 'onsc.cv.abstract.phone.validated'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'contact_person_telephone')]

    employee_id = fields.Many2one("hr.employee", string="Legajo", required=True, index=True, ondelete='cascade')
    name_contact = fields.Char(string=u'Nombre de persona de contacto', required=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # link_people_contact_id = fields.Many2one("model", u"Vínculo con persona de contacto", required=True)
    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]), required=True)
    contact_person_telephone = fields.Char(string=u'Teléfono de persona de contacto', required=True)
    phone_full = fields.Char(compute='_compute_phone_full', string=u'Teléfono de persona de contacto')
    remark_contact_person = fields.Text(string=u'Observación para la persona de contacto', required=True)

    @api.depends('prefix_phone_id', 'contact_person_telephone')
    def _compute_phone_full(self):
        for rec in self:
            rec.phone_full = '+%s %s' % (rec.prefix_phone_id.prefix_code, rec.contact_person_telephone)
