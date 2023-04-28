# -*- coding:utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response, \
    calc_full_name as calc_full_name


class ONSCLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.alta.vl'
    _inherit = ['onsc.legajo.alta.vl', 'onsc.cv.common.data']
    _description = 'Alta de vínculo laboral'
    _rec_name = 'full_name'

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    partner_id = fields.Many2one("res.partner", string="Contacto",
                                 domain=[('is_partner_cv', '=', True), ('is_cv_uruguay', '=', True)])
    cv_birthdate = fields.Date(string=u'Fecha de nacimiento', copy=False)
    cv_sex = fields.Selection(string=u'Sexo', copy=False)
    personal_phone = fields.Char(string="Teléfono Alternativo", related='partner_id.phone')
    mobile_phone = fields.Char(string="Teléfono Móvil", related='partner_id.mobile')
    email = fields.Char(string="e-mail", related='partner_id.email')
    cv_address_state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string='Departamento')
    cv_address_location_id = fields.Many2one('onsc.cv.location', related='partner_id.cv_location_id',
                                             string="Localidad")
    cv_address_nro_door = fields.Char(string="Número de puerta", related='partner_id.cv_nro_door')
    cv_address_is_cv_bis = fields.Boolean(string="Bis", related='partner_id.is_cv_bis')
    cv_address_apto = fields.Char(string="Apartamento", related='partner_id.cv_apto', )
    cv_address_place = fields.Text(string="Paraje", related='partner_id.cv_address_place')
    cv_address_zip = fields.Char(related='partner_id.zip', string="Código Postal")
    cv_address_block = fields.Char(related='partner_id.cv_address_block', string="Manzana")
    cv_address_sandlot = fields.Char(related='partner_id.cv_address_sandlot', string="Solar")
    employee_id = fields.Many2one('hr.employee', 'Employee')
    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital", related='employee_id.cv_digital_id', store=True)
    is_docket = fields.Boolean(string="Tiene legajo", related='cv_digital_id.is_docket')
    vacante_ids = fields.One2many('onsc.cv.digital.vacante', 'alta_vl_id', string="Vacantes")
    error_message_synchronization = fields.Char(string="Mensaje de Error", copy=False)
    is_error_synchronization = fields.Boolean(copy=False)

    def action_call_ws1(self):
        return self.syncronize(log_info=True)

    def action_call_ws4(self):
        return warning_response("No implementado")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
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
                record.country_of_birth_id = employee.cv_digital_id.country_of_birth_id
                record.marital_status_id = employee.cv_digital_id.marital_status_id
                record.uy_citizenship = employee.cv_digital_id.uy_citizenship
                record.crendencial_serie = employee.cv_digital_id.crendencial_serie
                record.credential_number = employee.cv_digital_id.credential_number
                record.personal_phone = employee.cv_digital_id.personal_phone
                record.mobile_phone = employee.cv_digital_id.mobile_phone
                record.email = employee.cv_digital_id.email
                record.cv_address_street_id = employee.cv_digital_id.cv_address_street_id

    @api.depends('partner_id')
    def _compute_full_name(self):
        for record in self:
            full_name = calc_full_name(record.partner_id.cv_first_name, record.partner_id.cv_second_name,
                                       record.partner_id.cv_last_name_1, record.partner_id.cv_last_name_2)
            if full_name:
                record.full_name = full_name
            else:
                record.full_name = 'New'

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
                vals.update(
                    {
                        'cv_birthdate': rec.cv_birthdate,
                    }
                )
            if rec.employee_id.cv_sex != rec.cv_sex:
                vals.update(
                    {
                        'cv_sex': rec.cv_sex
                    }
                )
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

    @api.onchange('descriptor1_id', 'descriptor2_id', 'regime_id', 'is_reserva_sgh', 'program_id', 'project_id',
                  'nroPuesto', 'nroPlaza')
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
                        # TODO ver si se puede hacer con un update de los campos sin borrar las vacantes
                        # data = {}
                        # if vacante_id.nroPuesto and not record.nroPuesto:
                        #     data.update({'nroPuesto': vacante_id.nroPuesto})
                        # if vacante_id.nroPlaza and not record.nroPlaza:
                        #     data.update({'nroPlaza': vacante_id.nroPlaza})
                        # if vacante_id.descriptor3_id and not record.descriptor3_id:
                        #     data.update({'descriptor3_id': vacante_id.descriptor3_id.id})
                        # if vacante_id.descriptor4_id and not record.descriptor4_id:
                        #     data.update({'descriptor4_id': vacante_id.descriptor4_id.id})
                        # if vacante_id.regime_id and not record.regime_id:
                        #     data.update({'regime_id': vacante_id.regime_id.id})
                        # record.update(data)

    @api.model
    def syncronize(self, log_info=False):
        if self.is_reserva_sgh and not (
                self.date_start and self.program_id and self.project_id and self.nroPuesto and self.nroPlaza):
            raise ValidationError(
                _("Los campos Fecha de Inicio, Programa, Proyecto, Nro. de Puesto y Nro. de Plaza son obligatorios para Buscar Vacantes"))
        if not self.is_reserva_sgh and not (
                self.date_start and self.program_id and self.project_id and self.regime_id and self.descriptor1_id and self.descriptor2_id and self.partner_id):
            raise ValidationError(
                _("Los campos Fecha de Inicio, Programa, Proyecto, Régimen, Descriptor 1 ,Descriptor 2 y CI son obligatorios para Buscar Vacantes"))

        response = self.env['onsc.legajo.abstract.alta.vl.ws1'].with_context(
            log_info=log_info).suspend_security().syncronize(self)
        if not isinstance(response, str):
            self.vacante_ids = response
        elif isinstance(response, str):
            return warning_response(response)
