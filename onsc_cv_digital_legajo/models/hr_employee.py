# -*- coding: utf-8 -*-

from odoo.addons.onsc_cv_digital.models.abstracts.onsc_cv_abstract_common import SELECTION_RADIO as SELECTION_RADIO
from odoo.addons.onsc_cv_digital.models.abstracts.onsc_cv_abstract_common import SITUATION as SITUATION

from odoo import models, fields, api
from .abstracts.onsc_cv_legajo_abstract_common import BLOOD_TYPE as BLOOD_TYPE

DISABILITE = u'¿Está inscripto en el registro de personas con discapacidad del Ministerio de Desarrollo Social?'

HISTORY_COLUMNS = [
    'cv_nro_doc',
    'cv_expiration_date',
    'marital_status_id',
    'status_civil_date',
    'cv_gender_id',
    'gender_date',
    'is_afro_descendants',
    'afro_descendant_date',
    'is_occupational_health_card',
    'occupational_health_card_date',
    'medical_aptitude_certificate_date',
    'people_disabilitie',
    'certificate_date',
    'to_date',
    'health_department_id',
    'name_contact',
    'contact_person_telephone',
    'remark_contact_person',
    'disability_date',
    'cv_first_race_id',
    'cv_address_street_id',
    'cv_address_street2_id',
    'cv_address_street3_id',
    'is_victim_violent',
    'type_support_ids',
    'remark_contact_person',
    'cv_race_ids',
    'cv_race2',
    'cv_sex',
    'cv_birthdate',
    'cv_first_name',
    'cv_second_name',
    'cv_last_name_1',
    'cv_last_name_2',
    'email',
    'cv_sex_updated_date'
]


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.cv.common.data', 'onsc.cv.legajo.abstract.common']
    _history_columns = HISTORY_COLUMNS

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_cv_digital_id',
                                    store=True)

    # -------- INFO DE CV QUE PASA DIRECTO AL LEGAJO SIN VALIDACION
    is_need_other_support = fields.Boolean(store=True, history=True, related='cv_digital_id.is_need_other_support')

    marital_status_id = fields.Many2one(
        "onsc.cv.status.civil", string="Estado civil",
        store=True,
        history=True)
    cjppu_affiliate_number = fields.Integer(
        string="Numero de afiliado a la CJPPU",
        store=True,
        history=True)
    professional_resume = fields.Text(
        string="Resumen profesional",
        store=True,
        history=True)
    user_linkedIn = fields.Char(string="Usuario en LinkedIn",
                                store=True,
                                history=True)
    gender_public_visualization_date = fields.Date(
        string="Fecha información visualización pública de género",
        store=True,
        history=True)
    cv_address_amplification = fields.Text(
        u"Aclaraciones",
        store=True)
    lear = fields.Selection(
        selection=SELECTION_RADIO,
        string=u'Entender y/o aprender',
        store=True,
        history=True)
    type_support_ids = fields.Many2many('onsc.cv.type.support', string=u'Tipos de apoyo',
                                        related='cv_digital_id.type_support_ids')
    last_modification_date = fields.Date(string=u'Fecha última modificación', store=True,
                                         compute='_compute_last_modification_date', readonly=True)
    institutional_email = fields.Char(
        string=u'Correo electrónico institucional',
        store=True,
        history=True)
    blood_type = fields.Selection(
        BLOOD_TYPE,
        string=u'Tipo de sangre',
        store=True,
        history=True)
    # --------- END OF RELATED

    is_driver_license = fields.Boolean(
        string="¿Tiene licencia de conducir?",
        history=True)
    is_cv_gender_public = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?",
        history=True)

    is_public_information_victim_violent = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?",
        history=True)
    is_cv_race_public = fields.Boolean(
        string="¿Permite que su identidad étnico-racial se visualice en su CV?",
        history=True)
    allow_content_public = fields.Selection(
        selection=[('si', u'Si'), ('no', u'No')],
        string=u'¿Permite que el contenido de esta sección se visualice en su CV?',
        history=True)
    situation_disability = fields.Selection(
        selection=[('si', u'Si'), ('no', u'No')],
        string=SITUATION,
        history=True)
    see = fields.Selection(
        selection=SELECTION_RADIO, string=u'Ver, aún si usa anteojos o lentes',
        history=True)
    hear = fields.Selection(selection=SELECTION_RADIO, string=u'Oír, aún si usa audífono', history=True)
    walk = fields.Selection(selection=SELECTION_RADIO, string=u'Caminar o subir escalones', history=True)
    speak = fields.Selection(selection=SELECTION_RADIO, string=u'Hablar o comunicarse aún usando lengua de señas',
                             history=True)
    realize = fields.Selection(selection=SELECTION_RADIO,
                               string=u'Realizar tareas de cuidado personal como comer, bañarse o vestirse solo',
                               history=True)

    interaction = fields.Selection(selection=SELECTION_RADIO, string=u'Interactuar y/o relacionarse con otras personas',
                                   history=True)
    need_other_support = fields.Text(string=u"¿Necesita otro apoyo?", history=True)
    emergency_service_telephone = fields.Char(string=u'Teléfono del servicio de emergencia', history=True)
    health_department_id = fields.Many2one('res.country.state', string=u'Departamento del prestador de salud',
                                           history=True)
    health_provider_id = fields.Many2one("onsc.legajo.health.provider", u"Prestador de Salud", history=True)
    emergency_service_id = fields.Many2one("onsc.legajo.emergency", u"Servicio de emergencia móvil", history=True)
    other_information_official = fields.Text(
        string="Otra información del funcionario/a",
        history=True)
    # -------- INFO DE CV QUE PASA DIRECTO AL LEGAJO SIN VALIDACION

    drivers_license_ids = fields.One2many("onsc.legajo.driver.license",
                                          inverse_name="employee_id",
                                          string="Licencias de conducir",
                                          copy=True, history=True,
                                          history_fields="validation_date,category_id,license_file,license_filename")

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
    cv_address_location_id = fields.Many2one('onsc.cv.location', u'Localidad/Ciudad', history=True)

    # Datos del legajo
    information_contact_ids = fields.One2many('onsc.cv.legajo.information.contact', 'employee_id',
                                              string=u'Información de Contacto', history=True,
                                              history_fields="name_contact,contact_person_telephone,remark_contact_person")

    # LED SPRINT3
    # EXPERIENCIA LABORAL
    work_experience_ids = fields.One2many(
        "onsc.legajo.work.experience",
        inverse_name="employee_id",
        string="Experiencia laboral"
    )
    # TUTORIAS, ORIENTACIONES, SUPERVISIONES
    tutoring_orientation_supervision_ids = fields.One2many(
        'onsc.legajo.tutoring.orientation.supervision',
        inverse_name="employee_id",
        string="Tutorías, Orientaciones, Supervisiones"
    )
    # VOLUNTARIADO
    volunteering_ids = fields.One2many(
        "onsc.legajo.volunteering",
        inverse_name="employee_id",
        string="Voluntariado"
    )
    # DOCENCIA
    work_teaching_ids = fields.One2many(
        "onsc.legajo.work.teaching",
        inverse_name="employee_id",
        string="Docencia"
    )
    # PARTICIPACION EN EVENTOS
    participation_event_ids = fields.One2many(
        "onsc.legajo.participation.event",
        inverse_name="employee_id",
        string="Participación en eventos"
    )
    # Investigacion
    work_investigation_ids = fields.One2many(
        "onsc.legajo.work.investigation",
        inverse_name="legajo_id",
        string="Investigación"
    )

    # Tutorías, Orientaciones, Supervisiones
    publication_production_evaluation_ids = fields.One2many(
        "onsc.legajo.publication.production.evaluation",
        inverse_name="legajo_id",
        string="Publicación, Producción y Evaluación"
    )
    # Otra Informacion
    other_relevant_information_ids = fields.One2many(
        "onsc.legajo.relevant.information",
        inverse_name="legajo_id",
        string="Otra información relevante"
    )
    # FORMACION

    basic_formation_ids = fields.One2many(
        'onsc.legajo.basic.formation', string=u'Formación básica', inverse_name="legajo_id", )
    advanced_formation_ids = fields.One2many(
        'onsc.legajo.advanced.formation', string=u'Formación avanzada', inverse_name="legajo_id")
    # CURSOS
    course_ids = fields.One2many(
        'onsc.legajo.course.certificate',
        string="Cursos", inverse_name="legajo_id")

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

    @api.depends(lambda model: ('create_date', 'write_date') if model._log_access else ())
    def _compute_last_modification_date(self):
        if self._log_access:
            for record in self:
                record.last_modification_date = record.write_date or record.create_date or fields.Date.today()
        else:
            self.last_modification_date = fields.Date.today()

    def button_get_info_fromcv(self):
        for record in self:
            record.suspend_security().write(record._get_info_fromcv())

    def _get_driver_licences_orm(self):
        driver_licences_orm = [(5,)]
        for drivers_license in self.cv_digital_id.drivers_license_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated'):
            driver_licences_orm.append((0, 0, {
                'cv_driver_license_id': drivers_license.id,
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

    def _get_info_fromcv(self):
        record = self.sudo()
        vals = {
            'country_of_birth_id': record.cv_digital_id.country_of_birth_id.id,
            # Datos del legajo
            'emergency_service_id': record.cv_digital_id.emergency_service_id.id,
            'prefix_emergency_phone_id': record.cv_digital_id.prefix_emergency_phone_id.id,
            'emergency_service_telephone': record.cv_digital_id.emergency_service_telephone,
            'institutional_email': record.cv_digital_id.institutional_email,
            'digitized_document_file': record.cv_digital_id.digitized_document_file,
            'digitized_document_filename': record.cv_digital_id.digitized_document_filename,
            'health_department_id': record.cv_digital_id.health_department_id.id,
            'health_provider_id': record.cv_digital_id.health_provider_id.id,
            'cv_first_name': record.cv_digital_id.partner_id.cv_first_name,
            'cv_second_name': record.cv_digital_id.partner_id.cv_second_name,
            'cv_last_name_1': record.cv_digital_id.partner_id.cv_last_name_1,
            'cv_last_name_2': record.cv_digital_id.partner_id.cv_last_name_2,
            'cv_birthdate': record.cv_digital_id.partner_id.cv_birthdate,
            'cv_sex': record.cv_digital_id.partner_id.cv_sex,
            'cv_sex_updated_date': record.cv_digital_id.cv_sex_updated_date,
            'prefix_phone_id': record.cv_digital_id.prefix_phone_id.id,
            'prefix_mobile_phone_id': record.cv_digital_id.prefix_mobile_phone_id.id,
            'personal_phone': record.cv_digital_id.personal_phone,
            'mobile_phone': record.cv_digital_id.mobile_phone,
            'email': record.cv_digital_id.email,
            'cv_nro_doc': record.cv_digital_id.cv_nro_doc,
            'uy_citizenship': record.cv_digital_id.uy_citizenship,
            'allow_content_public': record.cv_digital_id.allow_content_public,
            'situation_disability': record.cv_digital_id.situation_disability,
            'see': record.cv_digital_id.see,
            'hear': record.cv_digital_id.hear,
            'walk': record.cv_digital_id.walk,
            'speak': record.cv_digital_id.speak,
            'realize': record.cv_digital_id.realize,
            'lear': record.cv_digital_id.lear,
            'interaction': record.cv_digital_id.interaction,
            'need_other_support': record.cv_digital_id.need_other_support,
            'is_need_other_support': record.cv_digital_id.is_need_other_support,
            'is_cv_gender_public': record.cv_digital_id.is_cv_gender_public,
            'is_cv_race_public': record.cv_digital_id.is_cv_race_public,
            'other_information_official': record.cv_digital_id.other_information_official,
            'is_driver_license': record.cv_digital_id.is_driver_license,
            'is_public_information_victim_violent': record.cv_digital_id.is_public_information_victim_violent,
        }
        # SI NO TIENE LICENCIA ES PORQUE ES FUNCIONARIO NUEVO O DIRECTAMENTE EL CV NO TIENE LICENCIAS
        if len(record.drivers_license_ids) == 0:
            vals.update({'drivers_license_ids': record._get_driver_licences_orm()})
        # LO MISMO QUE LICENCIA DE CONDUCIR
        if len(record.information_contact_ids) == 0:
            vals.update({'information_contact_ids': record._get_information_contact_orm()})
        cv_address_documentary_validated = record.cv_digital_id.cv_address_documentary_validation_state == 'validated'
        if not self._context.get('exclusive_validated_info') or cv_address_documentary_validated:
            vals.update(record._get_info_fromcv_cv_address())
        # NRO DOCUMENTO
        if record.cv_digital_id.nro_doc_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_nrodoc())
        # PHOTO
        if record.cv_digital_id.photo_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_photo())
        # ESTADO CIVIL
        if record.cv_digital_id.marital_status_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_marital_status())
        # CREDENCIAL CIVICA
        if record.cv_digital_id.civical_credential_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_civical_credential())
        # GENERO
        if record.cv_digital_id.gender_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_gender())
        # IDENTIDAD ÉTNICO RACIAL
        if record.cv_digital_id.cv_race_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_race())
        # CARNET DE SALUD
        if record.cv_digital_id.occupational_health_card_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_occupational_health_card())
        # APTITUD MEDICA
        if record.cv_digital_id.medical_aptitude_certificate_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_occupational_medical_aptitud())
        # VICTIMA DELITOS VIOLENTOS
        if record.cv_digital_id.victim_violent_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_victim_violent())
        # DISCAPACIDAD
        if record.cv_digital_id.disabilitie_documentary_validation_state == 'validated':
            vals.update(record._get_info_fromcv_disabilitie())
        return vals

    def _get_info_fromcv_cv_address(self):
        # Domicilio
        return {
            'country_id': self.cv_digital_id.country_id.id,
            'cv_address_street': self.cv_digital_id.cv_address_street,
            'cv_address_street_id': self.cv_digital_id.cv_address_street_id.id,
            'cv_address_street2_id': self.cv_digital_id.cv_address_street2_id.id,
            'cv_address_street3_id': self.cv_digital_id.cv_address_street3_id.id,
            'cv_address_state_id': self.cv_digital_id.cv_address_state_id.id,
            'cv_address_location_id': self.cv_digital_id.cv_address_location_id.id,
            'cv_address_nro_door': self.cv_digital_id.cv_address_nro_door,
            'cv_address_apto': self.cv_digital_id.cv_address_apto,
            'cv_address_zip': self.cv_digital_id.cv_address_zip,
            'cv_address_is_cv_bis': self.cv_digital_id.cv_address_is_cv_bis,
            # 'cv_address_amplification': self.cv_digital_id.cv_address_amplification,
            'cv_address_place': self.cv_digital_id.cv_address_place,
            'cv_address_block': self.cv_digital_id.cv_address_block,
            'cv_address_sandlot': self.cv_digital_id.cv_address_sandlot,
            'address_receipt_file': self.cv_digital_id.partner_id.address_receipt_file,
            'address_info_date': self.cv_digital_id.partner_id.address_info_date,
            'address_receipt_file_name': self.cv_digital_id.partner_id.address_receipt_file_name,
        }

    def _get_info_fromcv_nrodoc(self):
        # NRO DOCUMENTO
        return {
            'cv_expiration_date': self.cv_digital_id.cv_expiration_date,
            'document_identity_file': self.cv_digital_id.document_identity_file,
            'document_identity_filename': self.cv_digital_id.document_identity_filename,
        }

    def _get_info_fromcv_photo(self):
        # FOTO
        return {
            'image_1920': self.cv_digital_id.partner_id.image_1920,
            'photo_updated_date': self.cv_digital_id.partner_id.cv_photo_updated_date,
        }

    def _get_info_fromcv_marital_status(self):
        # ESTADO CIVIL
        return {
            # 'marital_status_id': self.cv_digital_id.marital_status_id.id,
            'digitized_document_file': self.cv_digital_id.digitized_document_file,
            'digitized_document_filename': self.cv_digital_id.digitized_document_filename,
            'status_civil_date': self.cv_digital_id.status_civil_date,
        }

    def _get_info_fromcv_civical_credential(self):
        # CREDENCIAL CIVICA
        return {
            'uy_citizenship': self.cv_digital_id.uy_citizenship,
            'crendencial_serie': self.cv_digital_id.crendencial_serie,
            'credential_number': self.cv_digital_id.credential_number,
            'civical_credential_file': self.cv_digital_id.civical_credential_file,
            'civical_credential_filename': self.cv_digital_id.civical_credential_filename,
        }

    def _get_info_fromcv_gender(self):
        # GENERO
        return {
            'cv_gender_id': self.cv_digital_id.cv_gender_id.id,
            'cv_gender2': self.cv_digital_id.cv_gender2,
            'cv_gender_record_file': self.cv_digital_id.cv_gender_record_file,
            'cv_gender_record_filename': self.cv_digital_id.cv_gender_record_filename,
            'gender_date': self.cv_digital_id.gender_date,
        }

    def _get_info_fromcv_race(self):
        # IDENTIDAD ÉTNICO RACIAL
        return {
            'cv_race2': self.cv_digital_id.cv_race2,
            'cv_race_ids': self.cv_digital_id.cv_race_ids,
            'cv_first_race_id': self.cv_digital_id.cv_first_race_id,
            'afro_descendants_filename': self.cv_digital_id.afro_descendants_filename,
            'afro_descendants_file': self.cv_digital_id.afro_descendants_file,
            'is_afro_descendants': self.cv_digital_id.is_afro_descendants,
            'afro_descendant_date': self.cv_digital_id.afro_descendant_date,
        }

    def _get_info_fromcv_occupational_health_card(self):
        # CARNET DE SALUD
        return {
            'is_occupational_health_card': self.cv_digital_id.is_occupational_health_card,
            'occupational_health_card_date': self.cv_digital_id.occupational_health_card_date,
            'occupational_health_card_file': self.cv_digital_id.occupational_health_card_file,
            'occupational_health_card_filename': self.cv_digital_id.occupational_health_card_filename,
        }

    def _get_info_fromcv_occupational_medical_aptitud(self):
        # APTITUD MEDICA
        return {
            'is_medical_aptitude_certificate_status': self.cv_digital_id.is_medical_aptitude_certificate_status,
            'medical_aptitude_certificate_date': self.cv_digital_id.medical_aptitude_certificate_date,
            'medical_aptitude_certificate_file': self.cv_digital_id.medical_aptitude_certificate_file,
            'medical_aptitude_certificate_filename': self.cv_digital_id.medical_aptitude_certificate_filename,
        }

    def _get_info_fromcv_victim_violent(self):
        # VICTIMA DELITOS VIOLENTOS
        return {
            'relationship_victim_violent_file': self.cv_digital_id.relationship_victim_violent_file,
            'is_victim_violent': self.cv_digital_id.is_victim_violent,
            'relationship_victim_violent_filename': self.cv_digital_id.relationship_victim_violent_filename,
        }

    def _get_info_fromcv_disabilitie(self):
        # DISCAPACIDAD
        return {
            'people_disabilitie': self.cv_digital_id.people_disabilitie,
            'document_certificate_file': self.cv_digital_id.document_certificate_file,
            'document_certificate_filename': self.cv_digital_id.document_certificate_filename,
            'certificate_date': self.cv_digital_id.certificate_date,
            'to_date': self.cv_digital_id.to_date,
            'disability_date': self.cv_digital_id.disability_date,
            'type_support_ids': self._get_type_support_orm(),
        }

    def _sync_user(self, user, employee_has_image=False):
        vals = super(HrEmployee, self)._sync_user(user, employee_has_image)
        if self._context.get('is_alta_vl') and vals.get('image_1920'):
            vals.pop('image_1920')
        return vals


class ONSCLegajoDriverLicense(models.Model):
    _name = 'onsc.legajo.driver.license'
    _inherit = 'onsc.cv.abstract.documentary.validation'
    _description = 'Licencia de conducir'

    cv_driver_license_id = fields.Many2one("onsc.cv.driver.license", string="Licencia de conducir del CV",
                                           required=True,
                                           index=True, ondelete='cascade')
    employee_id = fields.Many2one("hr.employee", string="Legajo", required=True, index=True, ondelete='cascade')
    validation_date = fields.Date("Fecha de vencimiento", required=True)
    category_id = fields.Many2one("onsc.cv.drivers.license.categories", "Categoría", required=True)
    license_file = fields.Binary("Documento digitalizado licencia de conducir")
    license_filename = fields.Char('Nombre del documento digital - Licencia de conducir')


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

    def button_documentary_reject(self):
        self.mapped('legajo_driver_license_id').suspend_security().unlink()
        return super(ONSCCVDigitalDriverLicense, self).button_documentary_reject()

    def button_documentary_tovalidate(self):
        self.mapped('legajo_driver_license_id').suspend_security().unlink()
        return super(ONSCCVDigitalDriverLicense, self).button_documentary_tovalidate()

    def sync_driver_license(self, employee_id):
        DriverLicense = self.env['onsc.legajo.driver.license'].suspend_security()
        dict_vals = {
            'validation_date': self.validation_date,
            'category_id': self.category_id.id,
            'license_file': self.license_file,
            'license_filename': self.license_filename,
            'documentary_validation_state': self.documentary_validation_state,
            'documentary_reject_reason': self.documentary_reject_reason,
            'documentary_validation_date': self.documentary_validation_date,
            'documentary_user_id': self.documentary_user_id.id,
        }
        if self.legajo_driver_license_id:
            self.legajo_driver_license_id.suspend_security().write(dict_vals)
        else:
            dict_vals.update({
                'cv_driver_license_id': self.id,
                'employee_id': employee_id.id,
            })
            legajo_driver_license_id = DriverLicense.create(dict_vals)
            self.write({'legajo_driver_license_id': legajo_driver_license_id.id})


class ONSCCVLegajoInformationContact(models.Model):
    _name = 'onsc.cv.legajo.information.contact'
    _description = 'Información de Contacto para el legajo'
    _inherit = 'onsc.cv.abstract.phone.validated'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'contact_person_telephone')]

    cv_information_contact_id = fields.Many2one("onsc.cv.information.contact", string="Información de Contacto de CV",
                                                required=True, index=True, ondelete='cascade')
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
