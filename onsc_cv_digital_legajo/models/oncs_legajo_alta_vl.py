# -*- coding:utf-8 -*-
import json

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.alta.vl'
    _inherit = ['onsc.legajo.alta.vl', 'onsc.cv.common.data']
    _description = 'Alta de vínculo laboral'

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_cv_digital_id',
                                    store=True)
    partner_id = fields.Many2one("res.partner", related="cv_digital_id.partner_id", string="Contacto")
    cv_birthdate = fields.Date(string=u'Fecha de nacimiento')
    cv_sex = fields.Selection(string=u'Sexo')
    personal_phone = fields.Char(string="Teléfono Alternativo", related='partner_id.phone')
    mobile_phone = fields.Char(string="Teléfono Móvil", related='partner_id.mobile')
    email = fields.Char(string="e-mail", related='partner_id.email')
    cv_address_state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string='Departamento')
    cv_address_location_id = fields.Many2one('onsc.cv.location', related='partner_id.cv_location_id', string="Localidad")
    cv_address_nro_door = fields.Char(string="Número de puerta", related='partner_id.cv_nro_door')
    cv_address_is_cv_bis = fields.Boolean(string="Bis", related='partner_id.is_cv_bis')
    cv_address_apto = fields.Char(string="Apartamento", related='partner_id.cv_apto',)
    cv_address_place = fields.Text(string="Paraje", related='partner_id.cv_address_place')
    cv_address_zip = fields.Char(related='partner_id.zip', string="Código Postal")
    cv_address_block = fields.Char(related='partner_id.cv_address_block', string="Manzana")
    cv_address_sandlot = fields.Char(related='partner_id.cv_address_sandlot', string="Solar")
    employee_id = fields.Many2one('hr.employee', 'Employee', compute="_compute_employee_id", store=True)
    vacante_ids = fields.One2many('onsc.cv.digital.vacantes', 'alta_vl_id', string="Vacantes")
    error_message_synchronization = fields.Char(string="Mensaje de Error")
    has_error_synchronization = fields.Boolean()
    see_more = fields.Boolean()

    def action_call_ws1(self):
        pass

    def action_call_ws4(self):
        for rec in self.filtered(lambda x: x.state in ['borrador', 'error_sgh']):
            pass

    @api.depends('cv_nro_doc')
    @api.onchange('cv_nro_doc')
    def _compute_cv_digital_id(self):
        CVDigital = self.env['onsc.cv.digital'].sudo()
        for record in self:
            record = record.sudo()
            country_id = self.env['res.country'].sudo().search([('code', '=', 'UY')], limit=1)
            document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')])
            record.cv_digital_id = CVDigital.search([
                ('cv_nro_doc', '=', record.cv_nro_doc),
                ('type', '=', 'cv'),
                ('cv_emissor_country_id', '=', country_id.id),
                ('cv_document_type_id', '=', document_type_id.id),
            ], limit=1)
            record.button_get_info_fromcv()

    @api.depends('cv_nro_doc')
    @api.onchange('cv_nro_doc')
    def _compute_employee_id(self):
        Employee = self.env['hr.employee'].sudo()
        for record in self:
            record = record.sudo()
            country_id = self.env['res.country'].sudo().search([('code', '=', 'UY')], limit=1)
            document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')])
            record.employee_id = Employee.search([
                ('cv_nro_doc', '=', record.cv_nro_doc),
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
