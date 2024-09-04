# -*- coding: utf-8 -*-

import logging
from odoo.addons.onsc_cv_digital.models.abstracts.onsc_cv_abstract_documentary_validation import \
    DOCUMENTARY_VALIDATION_STATES

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

EMPLOYEE_MODIFIED_FIELDS_TO_NOTIFY_SGH = [
    'cv_nro_doc',
    'full_name',
    'cv_full_name',
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_first_name',
    'cv_second_name',
    'marital_status_id',
    'cv_birthdate',
    'cv_sex',
    'country_of_birth_id',
    'personal_phone',
    'mobile_phone',
    'email',
    'health_provider_id'
]

EMPLOYEE_MODIFIED_FIELDS = [
    'cv_nro_doc',
    'full_name',
    'cv_full_name',
    'cv_last_name_1',
    'cv_last_name_2',
    'cv_first_name',
    'cv_second_name',
    'marital_status_id',
    'cv_birthdate',
    'cv_sex',
    'country_of_birth_id',
    'personal_phone',
    'mobile_phone',
    'email',
    'uy_citizenship',
    'allow_content_public',
    'situation_disability',
    'see',
    'hear',
    'walk',
    'speak',
    'realize',
    'lear',
    'interaction',
    'need_other_support',
    'is_need_other_support',
    'emergency_service_telephone',
    'emergency_service_id',
    'health_department_id',
    'health_provider_id',
    'is_cv_gender_public',
    'other_information_official',
    'is_driver_license',
    'is_public_information_victim_violent',
    'marital_status_id',
    'cjppu_affiliate_number',
    'professional_resume',
    'user_linkedIn',
    'cv_address_amplification',
    'lear',
    'institutional_email',
    'blood_type',
    'cv_gender_id',
    'cv_gender2',
    'gender_date',
    'cv_gender_record_file',
    'cv_gender_record_filename',
    'is_cv_gender_public',
    'cv_race_ids',
    'cv_race2',
    'cv_first_race_id',
    'is_cv_race_public',
    'is_afro_descendants',
    'afro_descendants_file',
    'afro_descendants_filename',
    'afro_descendant_date',
    'is_victim_violent',
    'relationship_victim_violent_file',
    'relationship_victim_violent_filename',

]


class ONSCCVDigital(models.Model):
    _name = 'onsc.cv.digital'
    _inherit = ['onsc.cv.digital', 'onsc.cv.legajo.abstract.common', 'onsc.legajo.abstract.legajo.security']

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_emergency_phone_id', 'emergency_service_telephone')]

    employee_id = fields.Many2one("hr.employee", string="Empleado", compute='_compute_employee_id', store=True)
    is_docket = fields.Boolean(string="Tiene legajo")
    is_docket_active = fields.Boolean(string="Tiene legajo activo", compute='_compute_is_docket_active', store=True)
    gender_public_visualization_date = fields.Date(string="Fecha información visualización pública de género",
                                                   compute='_compute_gender_public_visualization_date', store=True)
    address_info_date = fields.Date(string="Fecha de información domicilio",
                                    related='partner_id.address_info_date',
                                    readonly=False,
                                    store=True)
    address_receipt_file = fields.Binary(related='partner_id.address_receipt_file', readonly=False)
    address_receipt_file_name = fields.Char(related='partner_id.address_receipt_file_name', readonly=False)

    information_contact_ids = fields.One2many('onsc.cv.information.contact', 'cv_digital_id',
                                              string=u'Información de Contacto')

    # LEGAJO VALIDACION DOCUMENTAL
    # Estado civil
    marital_status_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    marital_status_write_date = fields.Datetime('Fecha de última modificación',
                                                index=True,
                                                default=lambda *a: fields.Datetime.now())
    marital_status_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                           tracking=True)
    marital_status_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    marital_status_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                         string="Usuario validación documental",
                                                         tracking=True)
    # Foto
    photo_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    photo_write_date = fields.Datetime('Fecha de última modificación',
                                       index=True,
                                       default=lambda *a: fields.Datetime.now())
    photo_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental', tracking=True)
    photo_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    photo_documentary_user_id = fields.Many2one(comodel_name="res.users", string="Usuario validación documental",
                                                tracking=True)
    # Genero
    is_cv_gender_record = fields.Boolean(u'Constancia', related='cv_gender_id.record', store=True)
    gender_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    gender_write_date = fields.Datetime('Fecha de última modificación',
                                        index=True,
                                        default=lambda *a: fields.Datetime.now())
    gender_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                   tracking=True)
    gender_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    gender_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                 string="Usuario validación documental",
                                                 tracking=True)

    # Indentidad etnico racial
    cv_race_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    cv_race_write_date = fields.Datetime('Fecha de última modificación',
                                         index=True,
                                         default=lambda *a: fields.Datetime.now())
    cv_race_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                    tracking=True)
    cv_race_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    cv_race_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                  string="Usuario validación documental",
                                                  tracking=True)
    is_cv_race_defined = fields.Boolean(
        string='Tiene definida al menos una Identidad étnico-racial',
        compute='_compute_is_cv_race_defined',
        store=True
    )

    afro_descendant_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    afro_descendant_write_date = fields.Datetime('Fecha de última modificación',
                                                 index=True,
                                                 default=lambda *a: fields.Datetime.now())
    afro_descendant_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                            tracking=True)
    afro_descendant_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    afro_descendant_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                          string="Usuario validación documental",
                                                          tracking=True)

    # Carné de salud laboral
    occupational_health_card_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    occupational_health_card_write_date = fields.Datetime('Fecha de última modificación',
                                                          index=True,
                                                          default=lambda *a: fields.Datetime.now())
    occupational_health_card_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                                     tracking=True)
    occupational_health_card_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    occupational_health_card_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                                   string="Usuario validación documental",
                                                                   tracking=True)

    # Certificado de aptitud médico-deportiva
    medical_aptitude_certificate_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    medical_aptitude_certificate_write_date = fields.Datetime('Fecha de última modificación',
                                                              index=True,
                                                              default=lambda *a: fields.Datetime.now())
    medical_aptitude_certificate_documentary_reject_reason = fields.Text(
        string=u'Motivo de rechazo validación documental',
        tracking=True)
    medical_aptitude_certificate_documentary_validation_date = fields.Date(u'Fecha validación documental',
                                                                           tracking=True)
    medical_aptitude_certificate_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                                       string="Usuario validación documental",
                                                                       tracking=True)

    # Víctima de delitos violentos
    victim_violent_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    victim_violent_write_date = fields.Datetime('Fecha de última modificación',
                                                index=True,
                                                default=lambda *a: fields.Datetime.now())
    victim_violent_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                           tracking=True)
    victim_violent_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    victim_violent_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                         string="Usuario validación documental",
                                                         tracking=True)

    # Domicilio
    is_cv_address_populated = fields.Boolean(
        "¿Está el domicilio con al menos una información?",
        compute='_compute_is_cv_address_populated', store=True)
    cv_address_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    cv_address_write_date = fields.Datetime('Fecha de última modificación',
                                            index=True,
                                            default=lambda *a: fields.Datetime.now())
    cv_address_documentary_reject_reason = fields.Text(string=u'Motivo de rechazo validación documental',
                                                       tracking=True)
    cv_address_documentary_validation_date = fields.Date(u'Fecha validación documental', tracking=True)
    cv_address_documentary_user_id = fields.Many2one(comodel_name="res.users",
                                                     string="Usuario validación documental",
                                                     tracking=True)

    legajo_gral_info_documentary_validation_state = fields.Selection(
        selection=DOCUMENTARY_VALIDATION_STATES,
        string="Estado de validación documental",
        compute='_compute_legajo_documentary_validation_state',
        store=True
    )

    legajo_documentary_validation_sections_tovalidate = fields.Char(
        string="Secciones por validar",
        compute='_compute_legajo_documentary_validation_state',
        store=True
    )

    is_validated_seccions_rolleables = fields.Boolean(
        string='¿Son las validaciones documentales rolleables?',
        compute='_compute_is_validated_seccions_rolleables',
        store=False
    )

    is_driver_license_readonly = fields.Boolean(compute='_compute_is_driver_license_readonly')

    cv_help_contacts = fields.Html(
        compute=lambda s: s._get_help('cv_help_contacts'),
        default=lambda s: s._get_help('cv_help_contacts', True))

    @api.depends('drivers_license_ids', 'is_driver_license')
    def _compute_is_driver_license_readonly(self):
        for rec in self:
            rec.is_driver_license_readonly = rec.is_driver_license and len(rec.drivers_license_ids) > 0


    @api.depends('is_cv_gender_public')
    def _compute_gender_public_visualization_date(self):
        for record in self:
            record.gender_public_visualization_date = fields.Date.today()

    @api.depends('cv_emissor_country_id', 'cv_document_type_id', 'cv_nro_doc', 'is_docket')
    def _compute_employee_id(self):
        Employee = self.env['hr.employee'].sudo()
        for record in self:
            record.employee_id = Employee.search([
                ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                ('cv_document_type_id', '=', record.cv_document_type_id.id),
                ('cv_nro_doc', '=', record.cv_nro_doc),
            ], limit=1)

    def _compute_is_validated_seccions_rolleables(self):
        for record in self:
            record.is_validated_seccions_rolleables = not (record.employee_id and
                                                           record.employee_id.legajo_state == 'active')

    @api.depends('employee_id', 'employee_id.legajo_state', 'is_docket')
    def _compute_is_docket_active(self):
        for record in self:
            record.is_docket_active = record.employee_id and record.employee_id.legajo_state == 'active'

    @api.depends('cv_race_ids')
    def _compute_is_cv_race_defined(self):
        for record in self:
            record.is_cv_race_defined = len(record.cv_race_ids) > 0

    @api.depends(lambda self: self._get_legajo_documentary_validation_models())
    def _compute_legajo_documentary_validation_state(self):
        documentary_values = {
            'civical_credential_documentary_validation_state': _('Credencial cívica'),
            'nro_doc_documentary_validation_state': _('Documento de identidad'),
            'disabilitie_documentary_validation_state': _('Discapacidad'),
            'photo_documentary_validation_state': _('Foto'),
            'occupational_health_card_documentary_validation_state': _('Carné de salud laboral'),
            'medical_aptitude_certificate_documentary_validation_state': _('Certificado de aptitud médico-deportiva'),
            'cv_address_documentary_validation_state': _('Domicilio'),
        }
        field_documentary_validation_models = self._get_legajo_documentary_validation_models()
        for record in self:
            sections_tovalidate = []
            for documentary_validation_model in field_documentary_validation_models:
                if '_ids' in documentary_validation_model:
                    documentary_states = eval("record.mapped('%s')" % documentary_validation_model)
                else:
                    documentary_states = eval("record.%s" % documentary_validation_model)
                if len(documentary_states) and 'to_validate' in documentary_states:
                    documentary_validation_model_split = documentary_validation_model.split('.')
                    if len(documentary_validation_model_split) == 2:
                        sections_tovalidate.append(
                            eval("record.%s._description" % documentary_validation_model_split[0]))
                    else:
                        section_value = documentary_values.get(documentary_validation_model, '')
                        if documentary_validation_model not in ['disabilitie_documentary_validation_state',
                                                                'civical_credential_documentary_validation_state']:
                            sections_tovalidate.append(section_value)
                        elif documentary_validation_model == 'disabilitie_documentary_validation_state' and \
                                record.situation_disability == 'si':
                            sections_tovalidate.append(section_value)
                        elif documentary_validation_model == 'civical_credential_documentary_validation_state' and \
                                record.is_civical_credential_populated:
                            sections_tovalidate.append(section_value)
            if len(sections_tovalidate) > 0:
                documentary_validation_state = 'to_validate'
            else:
                documentary_validation_state = 'validated'
            record.legajo_gral_info_documentary_validation_state = documentary_validation_state
            sections_tovalidate = list(dict.fromkeys(sections_tovalidate))
            sections_tovalidate.sort()
            record.legajo_documentary_validation_sections_tovalidate = ', '.join(sections_tovalidate)

    @api.depends('country_id', 'address_receipt_file', 'address_info_date', 'cv_address_state_id',
                 'cv_address_location_id', 'cv_address_street_id', 'cv_address_street2_id', 'cv_address_street3_id',
                 'cv_address_nro_door', 'cv_address_street', 'cv_address_is_cv_bis', 'cv_address_apto',
                 'cv_address_zip', 'cv_address_place', 'cv_address_block', 'cv_address_sandlot',
                 'cv_address_amplification')
    # flake8: noqa: E126
    def _compute_is_cv_address_populated(self):
        for record in self:
            record.is_cv_address_populated = record.country_id.id or record.address_receipt_file or \
                                             record.address_info_date or record.cv_address_state_id.id or \
                                             record.cv_address_location_id.id or record.cv_address_street_id.id or \
                                             record.cv_address_street2_id.id or record.cv_address_street3_id.id or \
                                             record.cv_address_nro_door or record.cv_address_street or \
                                             record.cv_address_is_cv_bis or record.cv_address_apto or \
                                             record.cv_address_zip or record.cv_address_place or \
                                             record.cv_address_block or record.cv_address_sandlot or \
                                             record.cv_address_amplification

    @api.onchange('is_docket')
    def onchange_is_docket(self):
        if self.is_docket is False:
            self.gender_date = False
            self.afro_descendant_date = False
            self.status_civil_date = False
            self.disability_date = False

    @api.onchange('is_occupational_health_card')
    def onchange_is_occupational_health_card(self):
        super(ONSCCVDigital, self).onchange_is_occupational_health_card()
        if self.is_occupational_health_card:
            self.occupational_health_card_documentary_validation_state = 'to_validate'

    @api.onchange('is_medical_aptitude_certificate_status')
    def onchange_is_medical_aptitude_certificate_status(self):
        super(ONSCCVDigital, self).onchange_is_medical_aptitude_certificate_status()
        if self.is_medical_aptitude_certificate_status:
            self.medical_aptitude_certificate_documentary_validation_state = 'to_validate'

    @api.onchange('is_cv_address_populated')
    def onchange_is_cv_address_populated(self):
        if self.is_cv_address_populated:
            self.cv_address_documentary_validation_state = 'to_validate'

    def write(self, vals):
        if self._context.get('no_update_employee_status', False) is False:
            self._update_employee_status(vals)
        return super(ONSCCVDigital, self).write(vals)

    def _update_employee_status(self, values):
        BaseUtils = self.env['onsc.base.utils'].sudo()
        employees = self.env['hr.employee']
        for record in self.filtered(lambda x: x.is_docket_active and x.employee_id and x.type == 'cv'):
            employee_values_to_write = {}
            values_filtered = BaseUtils.get_really_values_changed(record, values)
            for modified_field in EMPLOYEE_MODIFIED_FIELDS_TO_NOTIFY_SGH:
                if modified_field in values_filtered:
                    employees |= record.employee_id

            for key, value in values_filtered.items():
                if key in EMPLOYEE_MODIFIED_FIELDS:
                    employee_values_to_write[key] = value
                if key == 'is_cv_gender_public':
                    employee_values_to_write['gender_public_visualization_date'] = fields.Date.today()
            if len(employee_values_to_write.keys()):
                record.employee_id.suspend_security().write(employee_values_to_write)
        employees.suspend_security().write({'notify_sgh': True})

    def button_legajo_update_documentary_validation_sections_tovalidate(self):
        self._compute_legajo_documentary_validation_state()

    def button_documentary_tovalidate(self):
        if self._context.get('documentary_validation'):
            self.suspend_security()._legajo_update_documentary(
                self._context.get('documentary_validation'),
                'to_validate', '')

    def button_documentary_approve(self):
        if self._context.get('documentary_validation'):
            self.suspend_security()._legajo_update_documentary(
                self._context.get('documentary_validation'),
                'validated',
                '')
            self.suspend_security()._update_legajo_atdocumentary_validation()

    def button_documentary_reject(self):
        ctx = self._context.copy()
        ctx.update({
            'default_model_name': self._name,
            'default_res_id': len(self.ids) == 1 and self.id or 0,
            'is_documentary_reject': True
        })
        if ctx.get('tree_view_ref'):
            ctx.pop('tree_view_ref')
        if ctx.get('form_view_ref'):
            ctx.pop('form_view_ref')
        return {
            'name': _('Rechazo de validación documental'),
            'view_mode': 'form',
            'res_model': 'onsc.cv.reject.wizard',
            'target': 'new',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def validate_header_documentary_validation(self):
        for record in self.filtered(lambda x: x.type == 'cv').with_context(
                no_update_header_documentary_validation=True):
            # GENERO
            if record.gender_documentary_validation_state != 'validated' and (
                    record.cv_gender_id is False or record.cv_gender_id.record is False):
                record.gender_documentary_validation_state = 'validated'
            # PHOTO
            if record.photo_documentary_validation_state != 'validated' and record.image_1920 is False:
                record.photo_documentary_validation_state = 'validated'
            # IDENTIDAD ETNICO RACIAL
            if record.cv_race_documentary_validation_state != 'validated' and len(record.cv_race_ids.ids) == 0:
                record.cv_race_documentary_validation_state = 'validated'
            # AFRO
            if record.afro_descendant_documentary_validation_state != 'validated' and record.is_afro_descendants is False:
                record.afro_descendant_documentary_validation_state = 'validated'
            # CARNE SALUD LABORAL
            if record.occupational_health_card_documentary_validation_state != 'validated' and record.is_occupational_health_card is False:
                record.occupational_health_card_documentary_validation_state = 'validated'
            # APTITUD MEDICO DEPORTIVA
            if record.medical_aptitude_certificate_documentary_validation_state != 'validated' and record.is_medical_aptitude_certificate_status is False:
                record.medical_aptitude_certificate_documentary_validation_state = 'validated'
            # VICTIMA DE DELITOS VIOLENTOS
            if record.victim_violent_documentary_validation_state != 'validated' and record.is_victim_violent is False:
                record.victim_violent_documentary_validation_state = 'validated'
            # DISCAPACIDAD
            if record.disabilitie_documentary_validation_state != 'validated' and record.people_disabilitie != 'si':
                record.disabilitie_documentary_validation_state = 'validated'
            # DOMICILIO
            if not record.is_cv_address_populated and record.cv_address_documentary_validation_state != 'validated':
                record.cv_address_documentary_validation_state = 'validated'
            # CREDENCIAL CIVICA
            cc_state_no_validated = record.civical_credential_documentary_validation_state != 'validated'
            if record.uy_citizenship == 'extranjero' and cc_state_no_validated:
                record.civical_credential_documentary_validation_state = 'validated'


    def update_header_documentary_validation(self, values):
        image_1920 = values.get('image_1920')
        if image_1920:
            self.photo_documentary_validation_state = 'to_validate'
        # ESTADO CIVIL
        marital_status_id = values.get('marital_status_id')
        status_civil_date = values.get('status_civil_date')
        digitized_document_file = values.get('digitized_document_file')
        if marital_status_id or status_civil_date or digitized_document_file:
            self.marital_status_documentary_validation_state = 'to_validate'
            self.marital_status_write_date = fields.Datetime.now()

        # GENERO
        cv_gender_id = values.get('cv_gender_id')
        cv_gender_record_file = values.get('cv_gender_record_file')
        gender_date = values.get('gender_date')
        update_employee_gender = cv_gender_id or cv_gender_record_file or gender_date
        if update_employee_gender:
            for record in self.with_context(no_update_header_documentary_validation=True):
                if record.cv_gender_id.record is False:
                    record.gender_documentary_validation_state = 'validated'
            self.gender_write_date = fields.Datetime.now()

        # AFRODESCENDIENTES
        is_afro_descendants_in_values = 'is_afro_descendants' in values
        afro_descendant_date = values.get('afro_descendant_date')
        afro_descendant_file = values.get('afro_descendants_file')
        update_employee_afro = is_afro_descendants_in_values or afro_descendant_date or afro_descendant_file
        if update_employee_afro:
            for record in self.with_context(no_update_header_documentary_validation=True):
                is_afro_descendants = is_afro_descendants_in_values and values.get(
                    'is_afro_descendants') or record.is_afro_descendants
                if is_afro_descendants is False:
                    record.afro_descendant_documentary_validation_state = 'validated'
            self.afro_descendant_write_date = fields.Datetime.now()

        # CARNE SALUD LABORAL
        is_occupational_health_card_in_values = 'is_occupational_health_card' in values
        occupational_health_card_date = values.get('occupational_health_card_date')
        occupational_health_card_file = values.get('occupational_health_card_file')
        if is_occupational_health_card_in_values or occupational_health_card_date or occupational_health_card_file:
            for record in self.with_context(no_update_header_documentary_validation=True):
                is_occupational_health_card = is_occupational_health_card_in_values and values.get(
                    'is_occupational_health_card') or record.is_occupational_health_card
                if is_occupational_health_card is False:
                    record.is_occupational_health_card = False
                    record.occupational_health_card_date = False
                    record.occupational_health_card_file = False
                    record.occupational_health_card_filename = False
                    record.with_context(documentary_validation='occupational_health_card').button_documentary_approve()
                else:
                    record.occupational_health_card_documentary_validation_state = 'to_validate'
            self.occupational_health_card_write_date = fields.Datetime.now()

        # APTITUD MEDICO DEPORTIVA
        is_medical_aptitude_certificate_status_in_values = 'is_medical_aptitude_certificate_status' in values
        medical_aptitude_certificate_date = values.get('medical_aptitude_certificate_date')
        medical_aptitude_certificate_file = values.get('medical_aptitude_certificate_file')
        if is_medical_aptitude_certificate_status_in_values or medical_aptitude_certificate_date or medical_aptitude_certificate_file:
            for record in self.with_context(no_update_header_documentary_validation=True):
                is_medical_aptitude_certificate_status = is_medical_aptitude_certificate_status_in_values and values.get(
                    'is_medical_aptitude_certificate_status') or record.is_medical_aptitude_certificate_status
                if is_medical_aptitude_certificate_status is False:
                    record.is_medical_aptitude_certificate_status = False
                    record.medical_aptitude_certificate_date = False
                    record.medical_aptitude_certificate_file = False
                    record.medical_aptitude_certificate_filename = False
                    record.with_context(
                        documentary_validation='medical_aptitude_certificate').button_documentary_approve()
                else:
                    record.medical_aptitude_certificate_documentary_validation_state = 'to_validate'
            self.medical_aptitude_certificate_write_date = fields.Datetime.now()

        # DISCAPACIDAD
        is_situation_disability_in_values = 'people_disabilitie' in values
        document_certificate_file = values.get('document_certificate_file')
        certificate_date = values.get('certificate_date')
        to_date = values.get('to_date')
        disability_date = values.get('disability_date')
        if is_situation_disability_in_values or document_certificate_file or certificate_date or to_date or disability_date:
            for record in self.with_context(no_update_header_documentary_validation=True):
                is_situation_disability = is_situation_disability_in_values and values.get(
                    'people_disabilitie') == 'si' or record.people_disabilitie == 'si'
                if is_situation_disability is False:
                    record.document_certificate_file = False
                    record.document_certificate_filename = False
                    record.certificate_date = False
                    record.to_date = False
                    record.with_context(documentary_validation='disabilitie').button_documentary_approve()
                else:
                    record.disabilitie_documentary_validation_state = 'to_validate'
            self.disabilitie_write_date = fields.Datetime.now()

        # DOMICILIO
        country_id = 'country_id' in values
        address_receipt_file = 'address_receipt_file' in values
        address_info_date = 'address_info_date' in values
        cv_address_state_id = 'cv_address_state_id' in values
        cv_address_location_id = 'cv_address_location_id' in values
        cv_address_street = 'cv_address_street' in values
        cv_address_street_id = 'cv_address_street_id' in values
        cv_address_street2_id = 'cv_address_street2_id' in values
        cv_address_street3_id = 'cv_address_street3_id' in values
        cv_address_nro_door = 'cv_address_nro_door' in values
        cv_address_is_cv_bis = 'cv_address_is_cv_bis' in values
        cv_address_apto = 'cv_address_apto' in values
        cv_addres_apto = 'cv_addres_apto' in values
        cv_address_zip = 'cv_address_zip' in values
        cv_address_place = 'cv_address_place' in values
        cv_address_block = 'cv_address_block' in values
        cv_address_sandlot = 'cv_address_sandlot' in values
        if cv_address_nro_door or cv_address_is_cv_bis or cv_address_apto or country_id or address_receipt_file or address_info_date or cv_address_state_id or cv_address_location_id or cv_address_street_id or cv_address_street2_id or cv_address_street3_id or cv_addres_apto or cv_address_zip or cv_address_place or cv_address_block or cv_address_sandlot or cv_address_street:
            for record in self.with_context(no_update_header_documentary_validation=True):
                if not record.is_cv_address_populated and record.cv_address_documentary_validation_state != 'validated':
                    record.with_context(documentary_validation='cv_address').button_documentary_approve()
                else:
                    record.cv_address_documentary_validation_state = 'to_validate'
                    record.cv_address_write_date = fields.Datetime.now()

        super(ONSCCVDigital, self).update_header_documentary_validation(values)
        self._update_employee_atheader_documentary_validation(update_employee_gender, update_employee_afro)

    def _update_employee_atheader_documentary_validation(self,
                                                      update_employee_gender = False,
                                                      update_employee_afro = False):
        # ACUALIZANDO EMPLEADO SEGUN ESTADO DE VALIDACION DOCUMENTAL
        if not update_employee_afro and not update_employee_gender:
            return
        for record in self.with_context(no_update_header_documentary_validation=True):
            employee_id = record.employee_id.suspend_security()
            if record.is_docket_active and employee_id:
                employee_vals = {}
                if update_employee_gender and record.cv_gender_id.record is False:
                    employee_vals = {
                        'cv_gender_id': record.cv_gender_id.id,
                        'cv_gender_record_file': record.cv_gender_record_file,
                        'cv_gender_record_filename': record.cv_gender_record_filename,
                        'gender_date': record.gender_date,
                    }
                if update_employee_afro and not record.is_afro_descendants:
                    employee_vals.update({
                        'is_afro_descendants': False,
                        'afro_descendants_file': False,
                        'afro_descendants_filename': False,
                        'afro_descendant_date': False,
                    })
                if not record.is_civical_credential_populated:
                    employee_vals.update({
                        'crendencial_serie': False,
                        'credential_number': False,
                        'civical_credential_file': False,
                        'civical_credential_filename': False,
                    })
                if employee_vals:
                    employee_id.write(employee_vals)

    def documentary_reject(self, reject_reason):
        self._legajo_update_documentary(self._context.get('documentary_validation'), 'rejected', reject_reason)

    #   VALIDACION DOCUMENTAL DE LEGAJO
    def _update_legajo_atdocumentary_validation(self):
        seccion = self._context.get('documentary_validation', '')
        for record in self.filtered(lambda x: x.is_docket_active):
            employee_id = record.employee_id
            record = record.sudo()
            vals = {}
            # FOTO
            if seccion == 'photo':
                # no genera historico
                vals.update({
                    'avatar_128': record.avatar_128,
                    'image_1920': record.image_1920,
                    'photo_updated_date': fields.Date.today(),
                })
            # NRO DOCUMENTO
            elif seccion == 'nro_doc':
                # no genera historico
                vals.update({
                    'cv_nro_doc': record.cv_nro_doc,
                    'cv_expiration_date': record.cv_expiration_date,
                    'document_identity_file': record.document_identity_file,
                    'document_identity_filename': record.document_identity_filename,
                })
            # ESTADO CIVIL
            elif seccion == 'marital_status':
                # no genera historico
                vals.update({
                    'marital_status_id': record.marital_status_id.id,
                    'digitized_document_file': record.digitized_document_file,
                    'digitized_document_filename': record.digitized_document_filename,
                })
            # CREDENCIAL CIVICA
            elif seccion == 'civical_credential':
                vals.update({
                    'uy_citizenship': record.uy_citizenship,
                    'crendencial_serie': record.crendencial_serie,
                    'credential_number': record.credential_number,
                    'civical_credential_file': record.civical_credential_file,
                    'civical_credential_filename': record.civical_credential_filename,
                })
            # CARNE SALUD LABORAL
            elif seccion == 'occupational_health_card':
                vals.update({
                    'is_occupational_health_card': record.is_occupational_health_card,
                    'occupational_health_card_date': record.occupational_health_card_date,
                    'occupational_health_card_file': record.occupational_health_card_file,
                    'occupational_health_card_filename': record.occupational_health_card_filename,
                })
            # APTITUD MEDICA
            elif seccion == 'medical_aptitude_certificate':
                vals.update({
                    'is_medical_aptitude_certificate_status': record.is_medical_aptitude_certificate_status,
                    'medical_aptitude_certificate_date': record.medical_aptitude_certificate_date,
                    'medical_aptitude_certificate_file': record.medical_aptitude_certificate_file,
                    'medical_aptitude_certificate_filename': record.medical_aptitude_certificate_filename,
                })
            # DIRECCION
            elif seccion == 'cv_address':
                partner_vals = {
                    'country_id': record.country_id.id,
                    'state_id': record.cv_address_state_id.id,
                    'cv_location_id': record.cv_address_location_id.id,
                    'street': record.cv_address_street_id.display_name or record.cv_address_street,
                    'zip': record.cv_address_zip,
                    'cv_address_place': record.cv_address_place,
                    'cv_address_block': record.cv_address_block,
                    'cv_address_sandlot': record.cv_address_sandlot,
                    'cv_nro_door': record.cv_address_nro_door,
                    'is_cv_bis': record.cv_address_is_cv_bis,
                    'cv_apto': record.cv_address_apto,
                    'cv_amplification': record.cv_address_amplification,
                }
                record.suspend_security().partner_id.write(partner_vals)
                vals.update({
                    'country_id': record.country_id.id,
                    'address_info_date': record.address_info_date,
                    'cv_address_state_id': record.cv_address_state_id.id,
                    'cv_address_location_id': record.cv_address_location_id.id,
                    'cv_address_street_id': record.cv_address_street_id.id,
                    'cv_address_street2_id': record.cv_address_street2_id.id,
                    'cv_address_street3_id': record.cv_address_street3_id.id,
                    'cv_address_street': record.cv_address_street,
                    'cv_address_zip': record.cv_address_zip,
                    'cv_address_place': record.cv_address_place,
                    'cv_address_block': record.cv_address_block,
                    'cv_address_sandlot': record.cv_address_sandlot,
                    'address_receipt_file': record.address_receipt_file,
                    'address_receipt_file_name': record.address_receipt_file_name,
                    'cv_address_nro_door': record.cv_address_nro_door,
                    'cv_address_is_cv_bis': record.cv_address_is_cv_bis,
                    'cv_address_apto': record.cv_address_apto,
                    'cv_address_amplification': record.cv_address_amplification,
                })
            # DISCAPACIDAD
            elif seccion == 'disabilitie':
                vals.update({
                    'allow_content_public': record.allow_content_public,
                    'situation_disability': record.situation_disability,
                    'people_disabilitie': record.people_disabilitie,
                    'document_certificate_filename': record.document_certificate_filename,
                    'document_certificate_file': record.document_certificate_file,
                    'certificate_date': record.certificate_date,
                    'to_date': record.to_date,
                    'disability_date': record.disability_date,
                })
            employee_id.suspend_security().write(vals)

    def _legajo_update_documentary(self, documentary_field, state, reject_reason):
        Calls = self.env['onsc.cv.digital.call']
        _user_id = self._context.get('user_id', self.env.user.id)
        vals = {
            '%s_documentary_validation_state' % documentary_field: state,
            '%s_documentary_reject_reason' % documentary_field: reject_reason,
            '%s_documentary_validation_date' % documentary_field: fields.Datetime.now(),
            '%s_documentary_user_id' % documentary_field: _user_id,
        }
        if not self._context.get('no_update_cv_calls'):
            for record in self:
                calls = Calls.with_context(unactive_user_config=True).search([
                    ('cv_digital_origin_id', '=', record.id),
                    ('is_zip', '=', False),
                    ('preselected', '!=', 'no'),
                ])
                last_write_date = eval('record.%s_write_date' % documentary_field)
                custom_vals = vals.copy()
                custom_vals['%s_write_date' % documentary_field] = fields.Datetime.now()
                calls.filtered(lambda x: x.create_date >= last_write_date).write(custom_vals)
        self.write(vals)

    def _update_cv_digital_origin_documentary_values(self, documentary_field, vals):
        for record in self:
            cv_digital_origin_id = record.cv_digital_origin_id
            if cv_digital_origin_id and eval(
                    'cv_digital_origin_id.%s_write_date' % documentary_field) < record.create_date:
                cv_digital_origin_id.write(vals)

    def _check_todisable_dynamic_fields(self):
        return super(ONSCCVDigital, self)._check_todisable_dynamic_fields() or self.is_docket

    def _get_legajo_documentary_validation_models(self, only_fields=False):
        if not bool(self._context):
            return ['photo_documentary_validation_state',
                    'occupational_health_card_documentary_validation_state',
                    'medical_aptitude_certificate_documentary_validation_state',
                    'cv_address_documentary_validation_state',
                    'civical_credential_documentary_validation_state',
                    'nro_doc_documentary_validation_state',
                    'disabilitie_documentary_validation_state']
        configs = self.env['onsc.cv.documentary.validation.config'].with_context(is_legajo=True).get_config()
        if only_fields:
            validation_models = []
            for config in configs.filtered(lambda x: x.field_id):
                validation_models.append('%s' % config.field_id.name)
        else:
            validation_models = ['photo_documentary_validation_state',
                                 'occupational_health_card_documentary_validation_state',
                                 'medical_aptitude_certificate_documentary_validation_state',
                                 'cv_address_documentary_validation_state',
                                 'civical_credential_documentary_validation_state',
                                 'nro_doc_documentary_validation_state',
                                 'disabilitie_documentary_validation_state']
            for config in configs.filtered(lambda x: x.field_id):
                if config.model_id.model == 'onsc.cv.course.certificate':
                    validation_models.extend(['course_ids.documentary_validation_state',
                                              'certificate_ids.documentary_validation_state'])
                else:
                    validation_models.append('%s.documentary_validation_state' % config.field_id.name)
        return validation_models

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_cv_digital_legajo.group_legajo_validador_doc_consulta')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_cv_digital_legajo.group_legajo_validador_doc_inciso')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_cv_digital_legajo.group_legajo_validador_doc_ue')

    # pylint: disable=W0102
    def cron_legajo_update_documentary_validation_sections_tovalidate(self, cv_ids=[]):
        """
        RECUPERACIÓN DE SECCIONES A VALIDAR SI CAMBIA LA CONFIGURACION
        """

        _logger.info("PROCESO DE SECCIONES A VALIDAR SI CAMBIA LA CONFIGURACION: INICIO")
        CVDigital = self.sudo().with_context(ignore_restrict=True)
        offset = self.env['ir.config_parameter'].sudo().get_param('parameter_cv_digital_sections2validate_offset')
        last_id = self.env['ir.config_parameter'].sudo().get_param('parameter_cv_digital_sections2validate_last_id')
        if len(cv_ids):
            cv_digitals = CVDigital.search([('type', '=', 'cv'), ('id', 'in', cv_ids)])
        else:
            cv_digitals = CVDigital.search([('type', '=', 'cv'), ('id', '>', int(last_id))], limit=int(offset))
        last_cv_digital = cv_digitals[-1]
        cv_digitals._compute_legajo_documentary_validation_state()
        self.env['ir.config_parameter'].sudo().set_param(
            'parameter_cv_digital_sections2validate_last_id',
            str(last_cv_digital.id))
        _logger.info("PROCESO DE SECCIONES A VALIDAR SI CAMBIA LA CONFIGURACION: FIN, ULTIMO ID: %s" % (str(last_cv_digital.id)))


class ONSCCVInformationContact(models.Model):
    _name = 'onsc.cv.information.contact'
    _description = 'Información de Contacto'
    _inherit = 'onsc.cv.abstract.phone.validated'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'contact_person_telephone')]

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV', required=True, index=True, ondelete='cascade')
    name_contact = fields.Char(string=u'Nombre de persona de contacto', required=True)
    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]), required=True)
    contact_person_telephone = fields.Char(string=u'Teléfono de persona de contacto', required=True)
    phone_full = fields.Char(compute='_compute_phone_full', string=u'Teléfono de persona de contacto')
    remark_contact_person = fields.Text(string=u'Observación para la persona de contacto', required=True)
    legajo_information_contact_id = fields.Many2one("onsc.cv.legajo.information.contact",
                                                    string="Información de Contacto de Legajo")

    @api.depends('prefix_phone_id', 'contact_person_telephone')
    def _compute_phone_full(self):
        for rec in self:
            rec.phone_full = '+%s %s' % (rec.prefix_phone_id.prefix_code, rec.contact_person_telephone)

    @api.model
    def create(self, values):
        record = super(ONSCCVInformationContact, self).create(values)
        employee_id = self.env['hr.employee'].suspend_security().search(
            [('cv_digital_id', '=', record.cv_digital_id.id)],
            limit=1)
        if employee_id:
            record.sync_legajo_information_contacto(employee_id)
        return record

    def write(self, vals):
        Employee = self.env['hr.employee'].suspend_security()
        result = super(ONSCCVInformationContact, self).write(vals)
        for record in self:
            employee_id = Employee.search([('cv_digital_id', '=', record.cv_digital_id.id)], limit=1)
            if employee_id:
                record.sync_legajo_information_contacto(employee_id)
        return result

    def sync_legajo_information_contacto(self, employee_id):
        LegajoInformationContact = self.env['onsc.cv.legajo.information.contact'].suspend_security()
        if self.legajo_information_contact_id:
            self.legajo_information_contact_id.suspend_security().write({
                'name_contact': self.name_contact,
                'prefix_phone_id': self.prefix_phone_id.id,
                'contact_person_telephone': self.contact_person_telephone,
                'phone_full': self.phone_full,
                'remark_contact_person': self.remark_contact_person
            })
        else:
            legajo_information_contact_id = LegajoInformationContact.create({
                'cv_information_contact_id': self.id,
                'employee_id': employee_id.id,
                'name_contact': self.name_contact,
                'prefix_phone_id': self.prefix_phone_id.id,
                'contact_person_telephone': self.contact_person_telephone,
                'phone_full': self.phone_full,
                'remark_contact_person': self.remark_contact_person
            })
            self.write({'legajo_information_contact_id': legajo_information_contact_id.id})
