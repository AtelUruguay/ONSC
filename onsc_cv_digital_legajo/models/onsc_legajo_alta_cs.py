# -*- coding: utf-8 -*-

import json

from odoo import models, fields, api

REQUIRED_FIELDS = ['date_start_commission', 'reason_description', 'norm_id', 'resolution_description',
                   'resolution_date', 'resolution_type', 'regime_commission_id']


class ONSCLegajoAltaCS(models.Model):
    _inherit = 'onsc.legajo.alta.cs'

    cv_digital_id = fields.Many2one(comodel_name="onsc.cv.digital",
                                    string="CV Digital",
                                    compute='_compute_employee_id',
                                    store=True)

    @api.depends('partner_id')
    def _compute_employee_id(self):
        Employee = self.env['hr.employee'].sudo()
        CVDigital = self.env['onsc.cv.digital'].sudo()
        for record in self:
            if record.partner_id:
                record.employee_id = Employee.search([
                    ('partner_id', '=', record.partner_id.id)
                ], limit=1)
                record.cv_digital_id = CVDigital.search([
                    ('cv_emissor_country_id', '=', record.partner_id.cv_emissor_country_id.id),
                    ('cv_document_type_id', '=', record.partner_id.cv_document_type_id.id),
                    ('cv_nro_doc', '=', record.partner_id.cv_nro_doc),
                    ('type', '=', 'cv')
                ], limit=1)
            else:
                record.employee_id = False
                record.cv_digital_id = False

    @api.depends('operating_unit_origin_id', 'is_inciso_origin_ac')
    def _compute_partner_id_domain(self):
        CVDigital = self.env['onsc.cv.digital'].sudo()
        user_partner_id = self.env.user.partner_id
        for record in self:
            if not record.operating_unit_origin_id:
                record.partner_id_domain = json.dumps([('id', 'in', [])])
            elif record.is_inciso_origin_ac:
                partner_ids = self.env['hr.contract'].sudo().search(
                    [('operating_unit_id', '=', record.operating_unit_origin_id.id),
                     ('legajo_state', '=', 'active'),
                     ('regime_id.presupuesto', '=', True)]).mapped('employee_id.partner_id').ids
                record.partner_id_domain = json.dumps([('id', 'in', partner_ids), ('id', '!=', user_partner_id.id)])
            else:
                partner_ids = CVDigital.search([
                    ('type', '=', 'cv'),
                    ('is_cv_uruguay', '=', True),
                    ('partner_id', '!=', record.partner_id.id)]).mapped('partner_id').ids
                record.partner_id_domain = json.dumps([('id', 'in', partner_ids)])

    @api.onchange('employee_id', 'cv_digital_id')
    def onchange_employee_id_cv_digital_id(self):
        if self.employee_id:
            self.cv_birthdate = self.employee_id.cv_birthdate
            self.cv_sex = self.employee_id.cv_sex
        elif self.cv_digital_id:
            self.cv_birthdate = self.cv_digital_id.cv_birthdate
            self.cv_sex = self.cv_digital_id.cv_sex
        else:
            self.cv_birthdate = False
            self.cv_sex = False

    def _get_legajo_employee(self):
        employee = super(ONSCLegajoAltaCS, self.with_context(is_alta_vl=True))._get_legajo_employee()
        cv = employee.cv_digital_id
        vals = employee.with_context(exclusive_validated_info=True)._get_info_fromcv()
        if cv.partner_id.user_ids:
            user_id = cv.partner_id.user_ids[0]
        else:
            user_id = cv.partner_id.user_id
        if cv and employee.user_id.id != user_id.id:
            vals['user_id'] = user_id.id
        if employee.cv_birthdate != self.cv_birthdate:
            vals.update({'cv_birthdate': self.cv_birthdate, })
        if employee.cv_sex != self.cv_sex:
            vals.update({'cv_sex': self.cv_sex})
        employee.suspend_security().write(vals)
        cv.activate_docket()
        return employee
