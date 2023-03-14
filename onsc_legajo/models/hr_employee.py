# -*- coding: utf-8 -*-

from odoo import models, fields, api


def calc_full_name(first_name, second_name, last_name_1, last_name_2):
    name_values = [first_name,
                   second_name,
                   last_name_1,
                   last_name_2]
    return ' '.join([x for x in name_values if x])


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.partner.common.data', 'model.history', 'mail.thread', 'mail.activity.mixin']
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

    def _set_binary_history(self, values):
        for rec in self:
            today = fields.Date.today()
            Attachment = self.env['ir.attachment']
            if values.get('document_identity_file') and rec.document_identity_file:
                Attachment.create({'name': rec.document_identity_filename + " " + str(today),
                                   'datas': rec.document_identity_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('civical_credential_file') and rec.civical_credential_file:
                Attachment.create({'name': rec.civical_credential_filename + " " + str(today),
                                   'datas': rec.civical_credential_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('cv_gender_record_file') and rec.cv_gender_record_file:
                Attachment.create({'name': rec.cv_gender_record_filename + " " + str(today),
                                   'datas': rec.cv_gender_record_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('afro_descendants_file') and rec.afro_descendants_file:
                Attachment.create({'name': rec.afro_descendants_filename + " " + str(today),
                                   'datas': rec.afro_descendants_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('occupational_health_card_file') and rec.occupational_health_card_file:
                Attachment.create({'name': rec.occupational_health_card_filename + " " + str(today),
                                   'datas': rec.occupational_health_card_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('medical_aptitude_certificate_file') and rec.medical_aptitude_certificate_file:
                Attachment.create({'name': rec.medical_aptitude_certificate_filename + " " + str(today),
                                   'datas': rec.medical_aptitude_certificate_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('relationship_victim_violent_file') and rec.relationship_victim_violent_file:
                Attachment.create({'name': rec.relationship_victim_violent_filename + " " + str(today),
                                   'datas': rec.relationship_victim_violent_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('address_receipt_file') and rec.address_receipt_file:
                Attachment.create({'name': rec.address_receipt_filename + " " + str(today),
                                   'datas': rec.address_receipt_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('document_certificate_file') and rec.document_certificate_file:
                Attachment.create({'name': rec.document_certificate_filename + " " + str(today),
                                   'datas': rec.document_certificate_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

            if values.get('digitized_document_file') and rec.digitized_document_file:
                Attachment.create({'name': rec.digitized_document_filename + " " + str(today),
                                   'datas': rec.digitized_document_file, 'res_model': 'hr.employee',
                                   'res_id': rec.id, 'type': 'binary'})

    def write(self, values):
        self._set_binary_history(values)
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
