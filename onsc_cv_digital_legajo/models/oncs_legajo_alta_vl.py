# -*- coding:utf-8 -*-
import json

from lxml import etree
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

# campos requeridos para la sincronización
required_fields = ['inciso_id', 'operating_unit_id', 'program_project_id', 'date_start', 'partner_id',
                   'reason_description', 'income_mechanism_id', 'norm_id', 'resolution_description', 'resolution_date',
                   'resolution_type', 'cv_birthdate', 'cv_sex', 'crendencial_serie', 'credential_number',
                   'retributive_day_id', 'occupation_id',
                   'date_income_public_administration', 'department_id', 'date_start', 'security_job_id']


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
        if view_type in ['form', 'tree', 'kanban'] and self.env.user.has_group(
                'onsc_legajo.group_legajo_alta_vl_consulta_altas_vl') and not self.env.user.has_group(
            'onsc_legajo.group_legajo_alta_vl_administrar_altas_vl'):
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
                tuple = (item['partner_id'][0], Partner.browse(partner_id)._custom_display_name())
                item['partner_id'] = tuple
            if item.get('program_project_id'):
                program_project_id = item['program_project_id'][0]
                tuple = (item['program_project_id'][0], Office.browse(program_project_id)._custom_display_name())
                item['program_project_id'] = tuple
            if item.get('retributive_day_id'):
                retributive_day_id = item['retributive_day_id'][0]
                tuple = (
                    item['retributive_day_id'][0], RetributiveDay.browse(retributive_day_id)._custom_display_name())
                item['retributive_day_id'] = tuple
            if item.get('norm_id'):
                norm_id = item['norm_id'][0]
                tuple = (item['norm_id'][0], LegajoNorm.browse(norm_id)._custom_display_name())
                item['norm_id'] = tuple
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
    cv_address_state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string='Departamento')
    cv_address_location_id = fields.Many2one('onsc.cv.location', related='partner_id.cv_location_id',
                                             string="Localidad")
    cv_address_street = fields.Char(related='partner_id.street', readonly=True)
    cv_address_nro_door = fields.Char(string="Número de puerta", related='partner_id.cv_nro_door')
    cv_address_is_cv_bis = fields.Boolean(string="Bis", related='partner_id.is_cv_bis')
    cv_address_apto = fields.Char(string="Apartamento", related='partner_id.cv_apto', )
    cv_address_place = fields.Text(string="Paraje", related='partner_id.cv_address_place')
    cv_address_zip = fields.Char(related='partner_id.zip', string="Código Postal")
    cv_address_block = fields.Char(related='partner_id.cv_address_block', string="Manzana")
    cv_address_sandlot = fields.Char(related='partner_id.cv_address_sandlot', string="Solar")
    employee_id = fields.Many2one('hr.employee', 'Employee')
    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital", string="Legajo Digital", copy=False)
    is_docket = fields.Boolean(string="Tiene legajo", related='cv_digital_id.is_docket')
    vacante_ids = fields.One2many('onsc.cv.digital.vacante', 'alta_vl_id', string="Vacantes")
    error_message_synchronization = fields.Char(string="Mensaje de Error", copy=False)
    is_error_synchronization = fields.Boolean(copy=False)
    codigoJornadaFormal = fields.Integer(string="Código Jornada Formal")
    is_ready_send_sgh = fields.Boolean(string="Listo para enviar", compute='_compute_is_ready_to_send')
    country_code = fields.Char("Código")

    def action_call_ws1(self):
        return self.syncronize_ws1(log_info=True)

    def action_call_ws4(self):
        return self.syncronize_ws4(log_info=True)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self._empty_fieldsVL()
        Employee = self.env['hr.employee'].sudo()
        for record in self.suspend_security():
            if record.partner_id:
                employee = Employee.search([
                    ('user_partner_id', '=', record.partner_id.id),
                    ('cv_emissor_country_id', '=', record.cv_emissor_country_id.id),
                    ('cv_document_type_id', '=', record.cv_document_type_id.id),
                ], limit=1)
                record.employee_id = employee.id
                record.cv_birthdate = employee.cv_digital_id.cv_birthdate
                record.cv_sex = employee.cv_digital_id.cv_sex
                CVDigital = self.env['onsc.cv.digital']
                cv_digital_id = CVDigital.search([
                    ('cv_emissor_country_id', '=', record.partner_id.cv_emissor_country_id.id),
                    ('cv_document_type_id', '=', record.partner_id.cv_document_type_id.id),
                    ('cv_nro_doc', '=', record.partner_id.cv_nro_doc),
                    ('type', '=', 'cv')
                ], limit=1)
                record.cv_digital_id = cv_digital_id
                record.country_code = cv_digital_id.partner_id.country_id.code
                record.country_of_birth_id = cv_digital_id.country_of_birth_id
                record.marital_status_id = cv_digital_id.marital_status_id
                record.uy_citizenship = cv_digital_id.uy_citizenship
                record.crendencial_serie = cv_digital_id.crendencial_serie
                record.credential_number = cv_digital_id.credential_number
                record.personal_phone = cv_digital_id.personal_phone
                record.mobile_phone = cv_digital_id.mobile_phone
                record.email = cv_digital_id.email
                record.cv_address_street_id = cv_digital_id.cv_address_street_id
                record.cv_address_street2_id = cv_digital_id.cv_address_street2_id
                record.cv_address_street3_id = cv_digital_id.cv_address_street3_id
                record.health_provider_id = cv_digital_id.health_provider_id

    @api.depends('partner_id')
    def _compute_full_name(self):
        for record in self:
            record.full_name = calc_full_name(
                record.partner_id.cv_first_name, record.partner_id.cv_second_name,
                record.partner_id.cv_last_name_1, record.partner_id.cv_last_name_2)

    @api.depends('inciso_id')
    def _compute_partner_id_domain(self):
        for record in self:
            domain = [('is_partner_cv', '=', True), ('is_cv_uruguay', '=', True),
                      ('id', '!=', self.env.user.partner_id.id)]
            self.partner_id_domain = json.dumps(domain)

    @api.depends('vacante_ids')
    def _compute_is_ready_to_send(self):
        for record in self:
            vacante = record.vacante_ids[:1]
            record.is_ready_send_sgh = bool(vacante and vacante.selected)

    def action_gafi_ok(self):
        """
        Cuando ha sido aprobado se impacta en el empleado y en el CV la fecha de nacimiento y el sexo
        si han sido modificado
        :return:
        """
        super(ONSCLegajoAltaVL, self).action_gafi_ok()
        for rec in self:
            vals = dict()
            if rec.employee_id.cv_birthdate != rec.cv_birthdate:
                vals.update({
                    'cv_birthdate': rec.cv_birthdate,
                })
            if rec.employee_id.cv_sex != rec.cv_sex:
                vals.update({
                    'cv_sex': rec.cv_sex
                })
            if vals:
                rec.employee_id.suspend_security().write(vals)
                rec.cv_digital_id.suspend_security().write(vals)

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
        self._check_required_fieds_ws4()
        response = self.env['onsc.legajo.abstract.alta.vl.ws4'].with_context(
            log_info=log_info).suspend_security().syncronize(self)
        if not isinstance(response, str):
            print(response)
            self.id_alta = response['pdaId']
            self.is_error_synchronization = False
            self.state = 'pendiente_auditoria_cgn'
        elif isinstance(response, str):
            self.is_error_synchronization = True
            self.state = 'error_sgh'
            self.error_message_synchronization = response

    def _check_required_fieds_ws4(self):
        for record in self:
            message = []
            for required_field in required_fields:
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
            if not record.attached_document_ids:
                message.append(_("Debe haber al menos un documento adjunto"))

        if message:
            fields_str = '\n'.join(message)
            message = 'Los siguientes campos son requeridos:  \n \n %s' % fields_str
            raise ValidationError(_(message))
        return True

    def _empty_fieldsVL(self):
        self.date_start = False
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
        self.reason_description = False
        self.norm_id = False
        self.resolution_description = False
        self.resolution_date = False
        self.resolution_type = False
        self.health_provider_id = False
        self.additional_information = False
        self.attached_document_ids = False
        self.id_alta = False
        self.income_mechanism_id = False
        self.cv_sex = False
        self.cv_birthdate = False
        self.cv_address_street_id = False
