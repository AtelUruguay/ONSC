# -*- coding:utf-8 -*-

from odoo import fields, models, api


class ONSCLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.alta.vl'
    _inherit = ['onsc.legajo.alta.vl', 'onsc.cv.common.data']
    _description = 'Alta de vínculo laboral'

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_cv_digital_id',
                                    store=True)
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
    employee_id = fields.Many2one('hr.employee', 'Employee', compute="_compute_employee_id", store=True)
    vacante_ids = fields.One2many('onsc.cv.digital.vacante', 'alta_vl_id', string="Vacantes")
    error_message_synchronization = fields.Char(string="Mensaje de Error", copy=False)
    is_error_synchronization = fields.Boolean(copy=False)
    is_see_more = fields.Boolean(copy=False)

    def action_call_ws1(self):
        self.syncronize(log_info=True)

    def action_call_ws4(self):
        for rec in self.filtered(lambda x: x.state in ['borrador', 'error_sgh']):
            pass

    @api.onchange('partner_id')
    def _compute_cv_digital_id(self):
        CVDigital = self.env['onsc.cv.digital'].sudo()
        for record in self:
            record = record.sudo()
            country_id = self.env['res.country'].sudo().search([('code', '=', 'UY')], limit=1)
            document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')])
            record.cv_digital_id = CVDigital.search([
                ('partner_id', '=', record.partner_id.id),
                ('type', '=', 'cv'),
                ('cv_emissor_country_id', '=', country_id.id),
                ('cv_document_type_id', '=', document_type_id.id),
            ], limit=1)
            vals = {
                'cv_first_name': record.partner_id.cv_first_name,
                'cv_second_name': record.partner_id.cv_second_name,
                'cv_last_name_1': record.partner_id.cv_last_name_1,
                'cv_last_name_2': record.partner_id.cv_last_name_2,
                'cv_birthdate': record.partner_id.cv_birthdate,
                'cv_sex': record.cv_digital_id.cv_sex,
                'cv_emissor_country_id': record.partner_id.cv_emissor_country_id.id,
                'cv_document_type_id': record.partner_id.cv_document_type_id.id,
                'country_of_birth_id': record.cv_digital_id.country_of_birth_id.id,
                'marital_status_id': record.cv_digital_id.marital_status_id.id,
                'uy_citizenship': record.cv_digital_id.uy_citizenship,
                'crendencial_serie': record.cv_digital_id.crendencial_serie,
                'credential_number': record.cv_digital_id.credential_number,
                'personal_phone': record.cv_digital_id.personal_phone,
                'mobile_phone': record.cv_digital_id.mobile_phone,
                'email': record.cv_digital_id.email,
                'cv_address_street_id': record.cv_digital_id.cv_address_street_id.id,
                'cv_address_nro_door': record.cv_digital_id.cv_address_nro_door,
                'cv_address_apto': record.cv_digital_id.cv_address_apto,
                'cv_address_zip': record.cv_digital_id.cv_address_zip,
                'cv_address_is_cv_bis': record.cv_digital_id.cv_address_is_cv_bis,
                'cv_address_place': record.cv_digital_id.cv_address_place,
            }
            record.suspend_security().write(vals)

    @api.onchange('partner_id')
    def _compute_employee_id(self):
        Employee = self.env['hr.employee'].sudo()
        for record in self:
            record = record.sudo()
            country_id = self.env['res.country'].sudo().search([('code', '=', 'UY')], limit=1)
            document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')])
            record.employee_id = Employee.search([
                ('user_partner_id', '=', record.partner_id.id),
                ('cv_emissor_country_id', '=', country_id.id),
                ('cv_document_type_id', '=', document_type_id.id),
            ], limit=1)

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
