# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.partner.common.data', 'model.history']
    _history_model = 'hr.employee.history'
    _history_columns = ['cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2', 'status_civil_date',
                        'uy_citizenship', 'cv_gender_id', 'gender_date', 'is_cv_gender_public', 'is_afro_descendants',
                        'afro_descendant_date', 'is_occupational_health_card', 'occupational_health_card_date',
                        'medical_aptitude_certificate_date', 'is_public_information_victim_violent',
                        'allow_content_public', 'situation_disability', 'people_disabilitie', 'certificate_date',
                        'to_date', 'see', 'hear', 'walk', 'speak', 'realize', 'lear', 'interaction',
                        'need_other_support', 'emergency_service_id', 'emergency_service_telephone',
                        'health_department_id', 'health_provider_id', 'blood_type', 'name_contact',
                        'contact_person_telephone', 'remark_contact_person', 'other_information_official'
                        ]
    # 'digitized_document_file', 'afro_descendants_file', 'cv_gender_record_file', 'document_identity_file', 'civical_credential_file', 'occupational_health_card_file'
    # 'relationship_victim_violent_file', 'document_certificate_file'

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    photo_updated_date = fields.Date(string="Fecha de foto de la/del funcionaria/o")
    cv_sex_updated_date = fields.Date(u'Fecha de información sexo')

    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]))
    personal_phone = fields.Char(string="Teléfono particular")
    prefix_mobile_phone_id = fields.Many2one('res.country.phone', 'Prefijo del móvil',
                                             default=lambda self: self.env['res.country.phone'].search(
                                                 [('country_id.code', '=', 'UY')]))
    mobile_phone = fields.Char(string="Teléfono celular")
    email = fields.Char(string="Email", history=True)

    @api.depends('cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2')
    def _compute_full_name(self):
        for record in self:
            full_name = calc_full_name(record.cv_first_name, record.cv_second_name,
                                       record.cv_last_name_1, record.cv_last_name_2)
            if full_name:
                record.full_name = full_name
            else:
                record.full_name = record.name

    @api.model
    def create(self, values):
        full_name = calc_full_name(values.get('cv_first_name'), values.get('cv_second_name'),
                                   values.get('cv_last_name_1'), values.get('cv_last_name_2'))
        if full_name:
            values['name'] = full_name
        elif self.env.context.get('is_legajo'):
            values['name'] = 'dummy'

        if self.env.context.get('is_legajo'):
            return super(HrEmployee, self.suspend_security()).create(values)
        else:
            return super(HrEmployee, self).create(values)

    def write(self, values):
        if self.env.context.get('is_legajo'):
            res = super(HrEmployee, self.suspend_security()).write(values)
        else:
            res = super(HrEmployee, self).write(values)
        for rec in self.filtered(lambda x: x.name != x.full_name and x.full_name):
            rec.name = rec.full_name
        return res

    def unlink(self):
        if self.env.context.get('is_legajo'):
            return super(HrEmployee, self.suspend_security()).unlink()
        else:
            return super(HrEmployee, self).unlink()

    @api.model
    def get_history_record_action(self, history_id, res_id):
        return super(HrEmployee, self.with_context(model_view_form_id=self.env.ref(
            'onsc_legajo.onsc_legajo_hr_employee_form').id)).get_history_record_action(history_id, res_id)


class HrEmployeeHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'hr.employee.history'
    _parent_model = 'hr.employee'
