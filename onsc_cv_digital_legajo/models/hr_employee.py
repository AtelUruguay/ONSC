# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.onsc_base.models.onsc_abstract_contact_common_data import CV_SEX as CV_SEX
from odoo.addons.onsc_cv_digital.models.abstracts.onsc_cv_abstract_common import SELECTION_RADIO as SELECTION_RADIO
from odoo.addons.onsc_cv_digital.models.abstracts.onsc_cv_abstract_common import SITUATION as SITUATION

DISABILITE = u'¿Está inscripto en el registro de personas con discapacidad del Ministerio de Desarrollo Social?'


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.cv.common.data', 'onsc.cv.legajo.abstract.common']
    _history_columns = [
        'image_1920', 'avatar_128', 'photo_updated_date', 'cv_nro_doc', 'cv_expiration_date', 'document_identity_file',
        'document_identity_filename', 'marital_status_id', 'digitized_document_file', 'digitized_document_filename',
        'cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2',
        'status_civil_date', 'uy_citizenship',
        'cv_gender_id', 'gender_date', 'is_cv_gender_public',
        'is_afro_descendants', 'afro_descendant_date',
        'is_occupational_health_card', 'occupational_health_card_date',
        'medical_aptitude_certificate_date', 'is_public_information_victim_violent',
        'allow_content_public', 'situation_disability',
        'people_disabilitie', 'certificate_date',
        'to_date', 'see', 'hear', 'walk', 'speak', 'realize', 'lear', 'interaction',
        'need_other_support', 'emergency_service_id', 'emergency_service_telephone',
        'health_department_id', 'health_provider_id', 'name_contact', 'contact_person_telephone',
        'remark_contact_person', 'other_information_official', 'disability_date', 'cv_first_race_id',
        'cv_address_street_id', 'cv_address_street2_id', 'cv_address_street3_id', 'is_victim_violent',
        'type_support_ids', 'remark_contact_person', 'cv_race_ids', 'cv_race2', 'is_cv_race_public'
    ]

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_cv_digital_id',
                                    store=True)

    # -------- INFO DE CV QUE PASA DIRECTO AL LEGAJO SIN VALIDACION
    cv_first_name = fields.Char(u'Primer nombre',
                                related='cv_digital_id.partner_id.cv_first_name',
                                store=True,
                                history=True)
    cv_second_name = fields.Char(u'Segundo nombre',
                                 related='cv_digital_id.partner_id.cv_second_name',
                                 store=True,
                                 history=True)
    cv_last_name_1 = fields.Char(u'Primer apellido',
                                 related='cv_digital_id.partner_id.cv_last_name_1',
                                 store=True,
                                 history=True)
    cv_last_name_2 = fields.Char(u'Segundo apellido',
                                 related='cv_digital_id.partner_id.cv_last_name_2',
                                 store=True,
                                 history=True)
    cv_birthdate = fields.Date(u'Fecha de nacimiento',
                               related='cv_digital_id.partner_id.cv_birthdate',
                               store=True,
                               history=True)
    cv_sex = fields.Selection(CV_SEX, u'Sexo',
                              related='cv_digital_id.partner_id.cv_sex',
                              store=True,
                              history=True)
    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      related='cv_digital_id.partner_id.prefix_phone_id', store=True, history=True)
    personal_phone = fields.Char(string="Teléfono particular", related='cv_digital_id.partner_id.phone', store=True,
                                 history=True)
    prefix_mobile_phone_id = fields.Many2one('res.country.phone', 'Prefijo del móvil',
                                             related='cv_digital_id.partner_id.prefix_mobile_phone_id', store=True,
                                             history=True)
    mobile_phone = fields.Char(string="Teléfono celular", related='cv_digital_id.partner_id.mobile', store=True,
                               history=True)
    email = fields.Char(string="Email", related='cv_digital_id.partner_id.email', store=True, history=True)
    uy_citizenship = fields.Selection(string="Ciudadanía uruguaya",
                                      related='cv_digital_id.uy_citizenship', store=True, history=True,
                                      selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                 ('extranjero', 'Extranjero')])

    cjppu_affiliate_number = fields.Integer(string="Numero de afiliado a la CJPPU",
                                            related='cv_digital_id.cjppu_affiliate_number', store=True, history=True)
    professional_resume = fields.Text(string="Resumen profesional", related='cv_digital_id.professional_resume',
                                      store=True, history=True)
    user_linkedIn = fields.Char(string="Usuario en LinkedIn", related='cv_digital_id.user_linkedIn', store=True,
                                history=True)
    is_cv_gender_public = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?",
        related='cv_digital_id.is_cv_gender_public', store=True, history=True)
    is_public_information_victim_violent = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?",
        related='cv_digital_id.is_public_information_victim_violent', store=True, history=True)
    is_cv_race_public = fields.Boolean(string="¿Permite que su identidad étnico-racial se visualice en su CV?",
                                       related='cv_digital_id.is_cv_race_public', store=True, history=True)

    allow_content_public = fields.Selection(selection=[('si', u'Si'), ('no', u'No')],
                                            string=u'¿Permite que el contenido de esta sección se visualice en su CV?',
                                            related='cv_digital_id.allow_content_public', store=True, history=True)
    situation_disability = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=SITUATION,
                                            related='cv_digital_id.situation_disability', store=True, history=True)
    see = fields.Selection(selection=SELECTION_RADIO, string=u'Ver, aún si usa anteojos o lentes',
                           related='cv_digital_id.see', store=True, history=True)
    hear = fields.Selection(selection=SELECTION_RADIO, string=u'Oír, aún si usa audífono', related='cv_digital_id.hear',
                            store=True, history=True)
    walk = fields.Selection(selection=SELECTION_RADIO, string=u'Caminar o subir escalones',
                            related='cv_digital_id.walk', store=True, history=True)
    speak = fields.Selection(selection=SELECTION_RADIO, string=u'Hablar o comunicarse aún usando lengua de señas',
                             related='cv_digital_id.speak', store=True, history=True)
    realize = fields.Selection(selection=SELECTION_RADIO,
                               string=u'Realizar tareas de cuidado personal como comer, bañarse o vestirse solo',
                               related='cv_digital_id.realize', store=True, history=True)
    lear = fields.Selection(selection=SELECTION_RADIO, string=u'Entender y/o aprender', related='cv_digital_id.lear',
                            store=True, history=True)
    interaction = fields.Selection(selection=SELECTION_RADIO, string=u'Interactuar y/o relacionarse con otras personas',
                                   related='cv_digital_id.interaction', store=True, history=True)
    need_other_support = fields.Text(string=u"¿Necesita otro apoyo?", related='cv_digital_id.need_other_support',
                                     store=True, history=True)
    is_need_other_support = fields.Boolean(compute='_compute_cv_type_support_domain',
                                           related='cv_digital_id.is_need_other_support')
    type_support_ids = fields.Many2many('onsc.cv.type.support', string=u'Tipos de apoyo',
                                        related='cv_digital_id.type_support_ids')
    last_modification_date = fields.Date(string=u'Fecha última modificación',
                                         related='cv_digital_id.last_modification_date')
    # -------- INFO DE CV QUE PASA DIRECTO AL LEGAJO SIN VALIDACION

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
        groups="hr.group_hr_user,onsc_legajo.group_legajo_configurador_empleado,onsc_base.group_base_onsc",
        tracking=True,
        history=True)
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
    address_info_date = fields.Date(string="Fecha de información domicilio",
                                    readonly=False,
                                    store=True)

    # Datos del legajo
    information_contact_ids = fields.One2many('onsc.cv.legajo.information.contact', 'employee_id',
                                              string=u'Información de Contacto', history=True,
                                              history_fields="contact_person_telephone,remark_contact_person")

    @api.depends('cv_emissor_country_id', 'cv_document_type_id', 'cv_nro_doc')
    def _compute_cv_digital_id(self):
        CVDigital = self.env['onsc.cv.digital']
        for record in self:
            record.cv_digital_id = CVDigital.search([
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
        for drivers_license in self.cv_digital_id.drivers_license_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated'):
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
                # 'cv_first_name': record.cv_digital_id.partner_id.cv_first_name,
                # 'cv_second_name': record.cv_digital_id.partner_id.cv_second_name,
                # 'cv_last_name_1': record.cv_digital_id.partner_id.cv_last_name_1,
                # 'cv_last_name_2': record.cv_digital_id.partner_id.cv_last_name_2,
                'photo_updated_date': record.cv_digital_id.partner_id.cv_photo_updated_date,
                # 'cv_birthdate': record.cv_digital_id.partner_id.cv_birthdate,
                'document_identity_file': record.cv_digital_id.document_identity_file,
                'document_identity_filename': record.cv_digital_id.document_identity_filename,
                # 'cv_sex': record.cv_digital_id.cv_sex,
                'cv_sex_updated_date': record.cv_digital_id.cv_sex_updated_date,
                # Datos personales
                'country_of_birth_id': record.cv_digital_id.country_of_birth_id.id,
                'marital_status_id': record.cv_digital_id.marital_status_id.id,
                # 'uy_citizenship': record.cv_digital_id.uy_citizenship,
                'crendencial_serie': record.cv_digital_id.crendencial_serie,
                'credential_number': record.cv_digital_id.credential_number,
                'civical_credential_file': record.cv_digital_id.civical_credential_file,
                'civical_credential_filename': record.cv_digital_id.civical_credential_filename,
                # 'prefix_phone_id': record.cv_digital_id.prefix_phone_id.id,
                # 'personal_phone': record.cv_digital_id.personal_phone,
                # 'prefix_mobile_phone_id': record.cv_digital_id.prefix_mobile_phone_id.id,
                # 'mobile_phone': record.cv_digital_id.mobile_phone,
                # 'email': record.cv_digital_id.email,
                # 'cjppu_affiliate_number': record.cv_digital_id.cjppu_affiliate_number,
                # 'professional_resume': record.cv_digital_id.professional_resume,
                # 'user_linkedIn': record.cv_digital_id.user_linkedIn,
                'is_driver_license': record.cv_digital_id.is_driver_license,
                'drivers_license_ids': record._get_driver_licences_orm(),
                'cv_expiration_date': record.cv_digital_id.cv_expiration_date,
                'status_civil_date': record.cv_digital_id.status_civil_date,
                # GENERO
                'cv_gender_id': record.cv_digital_id.cv_gender_id.id,
                'cv_gender2': record.cv_digital_id.cv_gender2,
                'cv_gender_record_file': record.cv_digital_id.cv_gender_record_file,
                'cv_gender_record_filename': record.cv_digital_id.cv_gender_record_filename,
                # 'is_cv_gender_public': record.cv_digital_id.is_cv_gender_public,
                'gender_date': record.cv_digital_id.gender_date,
                # RAZA
                'cv_race2': record.cv_digital_id.cv_race2,
                'cv_race_ids': record.cv_digital_id.cv_race_ids,
                'cv_first_race_id': record.cv_digital_id.cv_first_race_id,
                'afro_descendants_filename': record.cv_digital_id.afro_descendants_filename,
                'afro_descendants_file': record.cv_digital_id.afro_descendants_file,
                'is_afro_descendants': record.cv_digital_id.is_afro_descendants,
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
                # 'is_public_information_victim_violent': record.cv_digital_id.is_public_information_victim_violent,
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

                'address_info_date': record.cv_digital_id.partner_id.address_info_date,
                'address_receipt_file_name': record.cv_digital_id.partner_id.address_receipt_file_name,

                # Discapacidad
                # 'allow_content_public': record.cv_digital_id.allow_content_public,
                # 'situation_disability': record.cv_digital_id.situation_disability,
                'people_disabilitie': record.cv_digital_id.people_disabilitie,
                'document_certificate_file': record.cv_digital_id.document_certificate_file,
                'document_certificate_filename': record.cv_digital_id.document_certificate_filename,
                'certificate_date': record.cv_digital_id.certificate_date,
                'to_date': record.cv_digital_id.to_date,
                # 'see': record.cv_digital_id.see,
                # 'hear': record.cv_digital_id.hear,
                # 'walk': record.cv_digital_id.walk,
                # 'speak': record.cv_digital_id.speak,
                # 'realize': record.cv_digital_id.realize,
                # 'lear': record.cv_digital_id.lear,
                # 'interaction': record.cv_digital_id.interaction,
                # 'is_need_other_support': record.cv_digital_id.is_need_other_support,
                # 'need_other_support': record.cv_digital_id.need_other_support,
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
                # 'last_modification_date': record.cv_digital_id.last_modification_date,

            }
            record.suspend_security().write(vals)


class ONSCLegajoDriverLicense(models.Model):
    _name = 'onsc.legajo.driver.license'
    _description = 'Licencia de conducir'

    cv_driver_license_id = fields.Many2one("onsc.cv.driver.license", string="Licencia de conducir del CV", required=True,
                                           index=True, ondelete='cascade')
    employee_id = fields.Many2one("hr.employee", string="Legajo", required=True, index=True, ondelete='cascade')
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    license_file = fields.Binary("Documento digitalizado licencia de conducir")
    license_filename = fields.Char('Nombre del documento digital')

class ONSCCVDigitalDriverLicense(models.Model):
    _inherit = 'onsc.cv.driver.license'

    legajo_driver_license_id = fields.Many2one("onsc.legajo.driver.license", string="Licencia de conducir del Legajo")

    def button_documentary_approve(self):
        Employee = self.env['hr.employee'].suspend_security()
        result = super(ONSCCVDigitalDriverLicense, self).button_documentary_approve()
        for record in self:
            employee_id = Employee.search([('cv_digital_id', '=', record.cv_digital_id.id)], limit=1)
            if employee_id:
                record.sync_driver_license(employee_id)
        return result

    def sync_driver_license(self, employee_id):
        DriverLicense = self.env['onsc.legajo.driver.license'].suspend_security()
        if self.legajo_driver_license_id:
            self.legajo_driver_license_id.suspend_security().write({
                'validation_date': self.validation_date,
                'category_id': self.category_id.id,
                'license_file': self.license_file,
                'license_filename': self.license_filename
            })
        else:
            legajo_driver_license_id = DriverLicense.create({
                'cv_driver_license_id': self.id,
                'employee_id': employee_id.id,
                'validation_date': self.validation_date,
                'category_id': self.category_id.id,
                'license_file': self.license_file,
                'license_filename': self.license_filename
            })
            self.write({'legajo_driver_license_id': legajo_driver_license_id.id})



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
