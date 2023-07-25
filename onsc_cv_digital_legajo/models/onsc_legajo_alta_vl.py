# -*- coding:utf-8 -*-
import json

from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

# campos requeridos para la sincronización
REQUIRED_FIELDS = ['inciso_id', 'operating_unit_id', 'program_project_id', 'date_start', 'partner_id',
                   'reason_description', 'income_mechanism_id', 'norm_id', 'resolution_description', 'resolution_date',
                   'resolution_type', 'cv_birthdate', 'cv_sex', 'crendencial_serie', 'credential_number',
                   'retributive_day_id', 'occupation_id',
                   'date_income_public_administration', 'department_id', 'security_job_id']
name_doc_one = u'Documento digitalizado "Partida de matrimonio / Partida de unión concubinaria / '
name_doc_two = u'Certificado de convivencia / Partida o Certificado de divorcio / Partida de defunción'
digitized_document_full_name = f'{name_doc_one}{name_doc_two}'


class ONSCLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.alta.vl'
    _inherit = ['onsc.legajo.alta.vl', 'onsc.cv.common.data']
    _description = 'Alta de vínculo laboral'
    _rec_name = 'full_name'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajoAltaVL, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                            submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_alta_vl = self.env.user.has_group('onsc_legajo.group_legajo_alta_vl_consulta_altas_vl')
        is_user_administrar_altas_vl = self.env.user.has_group('onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')
        if view_type in ['form', 'tree', 'kanban'] and is_user_alta_vl and not is_user_administrar_altas_vl:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
            for node_form in doc.xpath("//button[@name='action_call_ws1']"):
                node_form.getparent().remove(node_form)
        res['arch'] = etree.tostring(doc)
        return res

    def read(self, fields=None, load="_classic_read"):
        Partner = self.env['res.partner'].sudo()
        Office = self.env['onsc.legajo.office'].sudo()
        RetributiveDay = self.env['onsc.legajo.jornada.retributiva'].sudo()
        LegajoNorm = self.env['onsc.legajo.norm'].sudo()
        result = super(ONSCLegajoAltaVL, self).read(fields, load)
        for item in result:
            if item.get('partner_id'):
                partner_id = item['partner_id'][0]
                item['partner_id'] = (item['partner_id'][0], Partner.browse(partner_id)._custom_display_name())
            if item.get('program_project_id'):
                program_project_id = item['program_project_id'][0]
                item['program_project_id'] = (
                    item['program_project_id'][0], Office.browse(program_project_id)._custom_display_name())
            if item.get('retributive_day_id'):
                retributive_day_id = item['retributive_day_id'][0]
                item['retributive_day_id'] = (
                    item['retributive_day_id'][0], RetributiveDay.browse(retributive_day_id)._custom_display_name())
            if item.get('norm_id'):
                norm_id = item['norm_id'][0]
                item['norm_id'] = (item['norm_id'][0], LegajoNorm.browse(norm_id)._custom_display_name())
        return result

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    partner_id = fields.Many2one("res.partner", string="Contacto", readonly=True,
                                 states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    partner_id_domain = fields.Char(string="Dominio Cliente", compute='_compute_partner_id_domain')
    cv_birthdate = fields.Date(string=u'Fecha de nacimiento', copy=False, readonly=True,
                               states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    cv_sex = fields.Selection(string=u'Sexo', copy=False, readonly=True,
                              states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    personal_phone = fields.Char(string="Teléfono Alternativo", related='partner_id.phone')
    mobile_phone = fields.Char(string="Teléfono Móvil", related='partner_id.mobile')
    email = fields.Char(string="e-mail", related='partner_id.email')
    digitized_document_file = fields.Binary(string=digitized_document_full_name)
    digitized_document_filename = fields.Char('Nombre del documento Digitalizado')

    cv_address_state_id = fields.Many2one('res.country.state', string='Departamento')
    cv_address_location_id = fields.Many2one('onsc.cv.location', string="Localidad")
    cv_address_street = fields.Char(string="Calle")
    cv_address_nro_door = fields.Char(string="Número de puerta")
    cv_address_is_cv_bis = fields.Boolean(string="Bis")
    cv_address_apto = fields.Char(string="Apartamento")
    cv_address_place = fields.Text(string="Paraje")
    cv_address_zip = fields.Char(string="Código Postal")
    cv_address_block = fields.Char(string="Manzana")
    cv_address_sandlot = fields.Char(string="Solar")
    address_receipt_file = fields.Binary('Documento digitalizado "Constancia de domicilio"')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')

    employee_id = fields.Many2one('hr.employee', 'Employee')
    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital", string="CV Digital", copy=False)
    is_docket = fields.Boolean(string="Tiene legajo", related='cv_digital_id.is_docket')
    vacante_ids = fields.One2many('onsc.cv.digital.vacante', 'alta_vl_id', string="Vacantes")
    codigoJornadaFormal = fields.Integer(string="Código Jornada Formal")
    country_code = fields.Char("Código")
    origin_type = fields.Selection([('M', 'Manual'), ('P', 'Proceso')], string='Origen',
                                   compute='_compute_origin_type', store=True)
    mass_upload_id = fields.Many2one('onsc.legajo.mass.upload.alta.vl', string='ID de ejecución')

    @api.depends('mass_upload_id')
    def _compute_origin_type(self):
        for record in self:
            if record.mass_upload_id:
                record.origin_type = 'P'
            else:
                record.origin_type = 'M'

    def action_call_ws1(self):
        return self.syncronize_ws1(log_info=True)

    def action_call_ws4(self):
        return self.syncronize_ws4(log_info=True)

    def action_aprobado_cgn(self):
        legajo = super(ONSCLegajoAltaVL, self).action_aprobado_cgn()
        vals = dict()
        if self.employee_id.cv_birthdate != self.cv_birthdate:
            vals.update({'cv_birthdate': self.cv_birthdate, })
        if self.employee_id.cv_sex != self.cv_sex:
            vals.update({'cv_sex': self.cv_sex})
        if vals:
            self.cv_digital_id.with_context(can_update_contact_cv=True).suspend_security().write(vals)
            self.employee_id.suspend_security().write(vals)
        return legajo

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self._empty_fieldsVL()
        self._update_altavl_info()

    def _update_altavl_info(self):
        Employee = self.env['hr.employee'].sudo()
        CVDigital = self.env['onsc.cv.digital'].sudo()
        for record in self.sudo():
            if record.partner_id:
                employee = Employee.search([
                    ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                    ('cv_document_type_id', '=', record.cv_document_type_id.id),
                    ('cv_nro_doc', '=', record.partner_id.cv_nro_doc),
                ], limit=1)
                cv_digital_id = CVDigital.sudo().search([
                    ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                    ('cv_document_type_id', '=', record.cv_document_type_id.id),
                    ('cv_nro_doc', '=', record.partner_id.cv_nro_doc),
                    ('type', '=', 'cv')
                ], limit=1)
                if employee:
                    record.employee_id = employee.id
                    record.cv_birthdate = employee.cv_birthdate
                    record.cv_sex = employee.cv_sex
                elif cv_digital_id and not self._context.get('no_update_extra'):
                    record.cv_birthdate = cv_digital_id.cv_birthdate
                    record.cv_sex = cv_digital_id.cv_sex

                record.cv_digital_id = cv_digital_id
                record.country_code = cv_digital_id.country_id.code
                record.country_of_birth_id = cv_digital_id.country_of_birth_id
                record.cv_address_state_id = cv_digital_id.cv_address_state_id
                record.cv_address_location_id = cv_digital_id.cv_address_location_id
                record.cv_address_street_id = cv_digital_id.cv_address_street_id
                record.cv_address_street2_id = cv_digital_id.cv_address_street2_id
                record.cv_address_street3_id = cv_digital_id.cv_address_street3_id
                record.cv_address_street = cv_digital_id.cv_address_street
                record.cv_address_nro_door = cv_digital_id.cv_address_nro_door
                record.cv_address_is_cv_bis = cv_digital_id.cv_address_is_cv_bis
                record.cv_address_apto = cv_digital_id.cv_address_apto
                record.cv_address_place = cv_digital_id.cv_address_place
                record.cv_address_zip = cv_digital_id.cv_address_zip
                record.cv_address_block = cv_digital_id.cv_address_block
                record.address_receipt_file = cv_digital_id.address_receipt_file
                record.address_receipt_file_name = cv_digital_id.address_receipt_file_name

                record.cv_expiration_date = cv_digital_id.cv_expiration_date
                record.document_identity_file = cv_digital_id.document_identity_file
                record.document_identity_filename = cv_digital_id.document_identity_filename
                record.civical_credential_file = cv_digital_id.civical_credential_file
                record.civical_credential_filename = cv_digital_id.civical_credential_filename
                record.digitized_document_file = cv_digital_id.digitized_document_file
                record.digitized_document_filename = cv_digital_id.digitized_document_filename

                record.marital_status_id = cv_digital_id.marital_status_id
                record.uy_citizenship = cv_digital_id.uy_citizenship
                record.crendencial_serie = cv_digital_id.crendencial_serie
                record.credential_number = cv_digital_id.credential_number
                record.personal_phone = cv_digital_id.personal_phone
                record.mobile_phone = cv_digital_id.mobile_phone
                record.email = cv_digital_id.email
                record.health_provider_id = cv_digital_id.health_provider_id

    @api.depends('partner_id')
    def _compute_full_name(self):
        for record in self:
            record.full_name = calc_full_name(
                record.partner_id.cv_first_name, record.partner_id.cv_second_name,
                record.partner_id.cv_last_name_1, record.partner_id.cv_last_name_2)

    @api.depends('inciso_id')
    def _compute_partner_id_domain(self):
        partner_ids = self.env['onsc.cv.digital'].search([
            ('type', '=', 'cv'),
            ('partner_id.is_partner_cv', '=', True),
            ('partner_id.is_cv_uruguay', '=', True),
            ('partner_id.id', '!=', self.env.user.partner_id.id)
        ]).mapped('partner_id.id')
        for record in self:
            record.partner_id_domain = json.dumps([('id', 'in', partner_ids)])

    @api.onchange('regime_id')
    def onchange_regimen(self):
        for rec in self:
            rec.descriptor1_id = False
            rec.descriptor2_id = False
            rec.descriptor3_id = False
            rec.descriptor4_id = False
            rec.contract_expiration_date = False
            rec.vacante_ids = False

    @api.onchange('descriptor1_id',
                  'descriptor2_id',
                  'regime_id',
                  'is_reserva_sgh',
                  'program_project_id',
                  'nroPuesto',
                  'nroPlaza')
    def onchange_clear_vacante_id(self):
        for rec in self:
            rec.vacante_ids = False

    @api.onchange('is_reserva_sgh')
    def onchange_is_reserva_sgh(self):
        for rec in self:
            rec.vacante_ids = False
            rec.descriptor1_id = False
            rec.descriptor2_id = False
            rec.regime_id = False
            rec.nroPuesto = False
            rec.nroPlaza = False

    @api.onchange('vacante_ids')
    def onchange_vacante_ids(self):
        for record in self:
            if record.vacante_ids:
                for vacante_id in record.vacante_ids:
                    if vacante_id.selected:
                        record.vacante_ids = vacante_id

    @api.model
    def syncronize_ws1(self, log_info=False):
        if self.is_reserva_sgh and not (
                self.date_start and self.program_project_id and self.nroPuesto and self.nroPlaza):
            raise ValidationError(
                _("Los campos Fecha de alta, Programa - Proyecto, Nro. de Puesto y Nro. de Plaza son obligatorios para buscar vacantes"))

        if not self.is_reserva_sgh and not (
                self.date_start and self.program_project_id and self.regime_id and self.descriptor1_id and self.descriptor2_id and self.partner_id):
            raise ValidationError(
                _("Los campos Fecha de alta, Programa - Proyecto, Régimen, Descriptor 1 ,Descriptor 2 y CI son obligatorios para buscar vacantes"))

        response = self.env['onsc.legajo.abstract.alta.vl.ws1'].with_context(
            log_info=log_info).suspend_security().syncronize(self)
        if not isinstance(response, str):
            self.vacante_ids = response
            self.is_error_synchronization = False
        elif isinstance(response, str):
            self.vacante_ids = False
            self.is_error_synchronization = True
            self.error_message_synchronization = response

    @api.model
    def syncronize_ws4(self, log_info=False):
        self.check_required_fields_ws4()
        self.env['onsc.legajo.abstract.alta.vl.ws4'].with_context(
            log_info=log_info).suspend_security().syncronize_multi(self)

    def action_call_multi_ws4(self):
        self.check_required_fields_ws4()
        if self.filtered(lambda x: x.state not in ['borrador', 'error_sgh']):
            raise ValidationError(_("Solo se pueden enviar altas en estado borrador o error SGH"))
        altas_presupuestales = self.filtered(lambda x: x.is_presupuestado)
        altas_presupuestales.syncronize_multi_ws4()
        altas_no_presupuestales = self.filtered(lambda x: not x.is_presupuestado)
        altas_no_presupuestales.syncronize_multi_ws4()
        return True

    def action_update_binary_fields(self):
        for record in self:
            record.document_identity_file = record.cv_digital_id.document_identity_file
            record.document_identity_filename = record.cv_digital_id.document_identity_filename
            record.civical_credential_file = record.cv_digital_id.civical_credential_file
            record.civical_credential_filename = record.cv_digital_id.civical_credential_filename
            record.digitized_document_file = record.cv_digital_id.digitized_document_file
            record.digitized_document_filename = record.cv_digital_id.digitized_document_filename

    def syncronize_multi_ws4(self):
        altas_vl_grouped = {}
        AltaVLWS4 = self.env['onsc.legajo.abstract.alta.vl.ws4'].sudo()
        for alta in self:
            inciso = alta.inciso_id
            unidad_ejecutora = alta.operating_unit_id
            clave = (inciso, unidad_ejecutora)
            if clave in altas_vl_grouped:
                altas_vl_grouped[clave] += alta
            else:
                altas_vl_grouped[clave] = alta
        for clave, altas_vl in altas_vl_grouped.items():
            AltaVLWS4.with_context(
                log_info=False).syncronize_multi(altas_vl)

    # flake8: noqa: C901
    def check_required_fields_ws4(self):
        for record in self:
            message = []
            for required_field in REQUIRED_FIELDS:
                if not eval('record.%s' % required_field):
                    message.append(record._fields[required_field].string)
            if record.is_indVencimiento and not record.contract_expiration_date:
                message.append(record._fields['contract_expiration_date'].string)
            if not record.partner_id.cv_last_name_1:
                message.append("Primer Apellido")
            if not record.partner_id.cv_first_name:
                message.append("Primer Nombre")
            if (record.is_reserva_sgh or record.is_presupuestado) and not record.vacante_ids.filtered(
                    lambda x: x.selected):
                if not record.nroPlaza or not record.nroPuesto:
                    message.append("Necesita seleccionar una vacante")
            if not record.is_reserva_sgh and not record.is_presupuestado and not record.descriptor3_id:
                message.append(record._fields['descriptor3_id'].string)
            if not record.is_reserva_sgh and not record.is_presupuestado and not record.regime_id:
                message.append(record._fields['regime_id'].string)
            if record.is_reserva_sgh and not record.nroPuesto:
                message.append(record._fields['nroPuesto'].string)
            if record.is_reserva_sgh and not record.nroPlaza:
                message.append(record._fields['nroPlaza'].string)
            if record.income_mechanism_id.is_call_number_required and not record.call_number:
                message.append(record._fields['call_number'].string)
            if not self.env.context.get('not_check_attached_document', False) and not record.attached_document_ids:
                message.append(_("Debe haber al menos un documento adjunto"))
            if record.health_provider_id and record.health_provider_id.code:
                try:
                    if len(str(int(record.health_provider_id.code))) >= 3:
                        message.append("El código de prestador de salud debe tener 3 dígitos")
                except ValueError:
                    message.append("El código de prestador de salud debe ser numérico")

            if record.is_responsable_uo and record.department_id:
                domain_alta = [
                    ('state', '=', 'pendiente_auditoria_cgn'),
                    ('department_id', '=', record.department_id.id),
                    ('is_responsable_uo', '=', True),
                ]
                count = self.sudo().search_count(domain_alta)
                if count:
                    message.append(
                        "Ya existe un alta de vínvulo laboral pendiente de auditoría para la UO seleccionada")
                if not count and record.department_id.manager_id:
                    message.append("La UO ya tiene un responsable")
        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))
        return True

    def _empty_fieldsVL(self):
        self.date_start = fields.Date.today()
        self.program_project_id = False
        self.nroPuesto = False
        self.nroPlaza = False
        self.regime_id = False
        self.descriptor1_id = False
        self.department_id = False
        self.retributive_day_id = False
        self.security_job_id = False
        self.occupation_id = False
        self.descriptor2_id = False
        self.descriptor3_id = False
        self.descriptor4_id = False
        self.date_income_public_administration = False
        self.inactivity_years = False
        self.graduation_date = False
        self.contract_expiration_date = False
        # self.reason_description = False
        # self.norm_id = False
        # self.resolution_description = False
        # self.resolution_date = False
        # self.resolution_type = False
        self.health_provider_id = False
        self.additional_information = False
        self.attached_document_ids = False
        self.id_alta = False
        self.income_mechanism_id = False
        self.cv_sex = False
        self.cv_birthdate = False
        self.cv_address_street_id = False

    def _get_legajo_employee(self):
        employee = super(ONSCLegajoAltaVL, self.with_context(is_alta_vl=True))._get_legajo_employee()
        cv = employee.cv_digital_id
        vals = employee._get_info_fromcv()
        vals.update({
            'cv_birthdate': self.cv_birthdate,
            'cv_sex': self.cv_sex,
        })
        if cv.partner_id.user_ids:
            user_id = cv.partner_id.user_ids[0]
        else:
            user_id = cv.partner_id.user_id
        if cv and employee.user_id.id != user_id.id:
            vals['user_id'] = user_id.id
        # DOMICILIO
        if cv and cv.cv_address_documentary_validation_state != 'validated':
            vals.update({
                'country_id': self.cv_emissor_country_id.id,
                'cv_address_street': self.cv_address_street,
                'cv_address_street_id': self.cv_address_street_id.id,
                'cv_address_street2_id': self.cv_address_street2_id.id,
                'cv_address_street3_id': self.cv_address_street3_id.id,
                'cv_address_state_id': self.cv_address_state_id.id,
                'cv_address_location_id': self.cv_address_location_id.id,
                'cv_address_nro_door': self.cv_address_nro_door,
                'cv_address_apto': self.cv_address_apto,
                'cv_address_zip': self.cv_address_zip,
                'cv_address_is_cv_bis': self.cv_address_is_cv_bis,
                'cv_address_place': self.cv_address_place,
                'cv_address_block': self.cv_address_block,
                'cv_address_sandlot': self.cv_address_sandlot,
                'address_receipt_file': self.address_receipt_file,
                'address_receipt_file_name': self.address_receipt_file_name,
            })
            if cv and self.create_date >= cv.cv_address_write_date:
                cv.with_context(documentary_validation='cv_address',
                                user_id=self.ws4_user_id.id,
                                can_update_contact_cv=True).button_documentary_approve()

        # CREDENCIAL CIVICA
        if cv and cv.civical_credential_documentary_validation_state != 'validated':
            vals.update({
                'uy_citizenship': self.uy_citizenship,
                'crendencial_serie': self.crendencial_serie,
                'credential_number': self.credential_number,
                'civical_credential_file': self.civical_credential_file,
                'civical_credential_filename': self.civical_credential_filename
            })
            if cv and self.create_date >= cv.civical_credential_write_date:
                cv.with_context(user_id=self.ws4_user_id.id,
                                documentary_validation='civical_credential').button_documentary_approve()
        # ESTADO CIVIL
        if cv and cv.marital_status_documentary_validation_state != 'validated':
            vals.update({
                'marital_status_id': self.marital_status_id.id,
                'digitized_document_file': self.digitized_document_file,
                'digitized_document_filename': self.digitized_document_filename,
            })
            if cv and self.create_date >= cv.marital_status_write_date:
                cv.with_context(user_id=self.ws4_user_id.id,
                                documentary_validation='marital_status').button_documentary_approve()
        # NRO DOCUMENTO
        if cv and cv.nro_doc_documentary_validation_state != 'validated':
            vals.update({
                'cv_expiration_date': self.cv_expiration_date,
                'document_identity_file': self.document_identity_file,
                'document_identity_filename': self.document_identity_filename,
            })
            if cv and self.create_date >= cv.nro_doc_write_date:
                cv.with_context(user_id=self.ws4_user_id.id,
                                documentary_validation='nro_doc').button_documentary_approve()
        employee.write(vals)
        cv.write({'is_docket': True})
        return employee

    # MAIL TEMPLATE UTILS
    def get_altavl_name(self):
        return self.with_context(show_cv_nro_doc=True).partner_id.name_get()[0][1]

    def _is_employee_notify_sgh_nedeed(self):
        values = {
            'country_of_birth_id': self.cv_digital_id.country_of_birth_id.id,
            'health_provider_id': self.cv_digital_id.health_provider_id.id,
            'uy_citizenship': self.cv_digital_id.uy_citizenship,
            'personal_phone': self.cv_digital_id.personal_phone,
            'mobile_phone': self.cv_digital_id.mobile_phone,
            'email': self.cv_digital_id.email
        }
        if self.cv_digital_id.civical_credential_documentary_validation_state == 'validated':
            values.update({
                'crendencial_serie': self.cv_digital_id.crendencial_serie,
                'credential_number': self.cv_digital_id.credential_number
            })
        if self.cv_digital_id.marital_status_documentary_validation_state == 'validated':
            values.update({
                'marital_status_id': self.cv_digital_id.marital_status_id.id,
            })
        if self.cv_digital_id.cv_address_documentary_validation_state == 'validated':
            values.update({
                'cv_address_location_id': self.cv_digital_id.cv_address_location_id.id,
                'cv_address_street': self.cv_digital_id.cv_address_street,
                'cv_address_street_id': self.cv_digital_id.cv_address_street_id.id,
                'cv_address_street2_id': self.cv_digital_id.cv_address_street2_id.id,
                'cv_address_street3_id': self.cv_digital_id.cv_address_street3_id.id,
                'cv_address_nro_door': self.cv_digital_id.cv_address_nro_door,
                'cv_address_is_cv_bis': self.cv_digital_id.cv_address_is_cv_bis,
                'cv_address_apto': self.cv_digital_id.cv_address_apto,
                'cv_address_place': self.cv_digital_id.cv_address_place,
                'cv_address_zip': self.cv_digital_id.cv_address_zip,
                'cv_address_block': self.cv_digital_id.cv_address_block,
                'cv_address_sandlot': self.cv_digital_id.cv_address_sandlot,
            })
        values_filtered = self.env['onsc.base.utils'].sudo().get_really_values_changed(self, values)
        return len(values_filtered.keys()) > 0

