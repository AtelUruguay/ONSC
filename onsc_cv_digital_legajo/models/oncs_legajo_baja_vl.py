# -*- coding:utf-8 -*-

from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api


class ONSCLegajoBajaVL(models.Model):
    _name = 'onsc.legajo.baja.vl'
    _inherit = ['onsc.legajo.baja.vl']
    _description = 'Baja de vínculo laboral'
    _rec_name = 'full_name'

    full_name = fields.Char('Nombre', compute='_compute_full_name')

    @api.depends('partner_id')
    def _compute_full_name(self):
        for record in self:
            record.full_name = record.partner_id.cv_nro_doc + ' - ' + calc_full_name(
                record.partner_id.cv_first_name, record.partner_id.cv_second_name,
                record.partner_id.cv_last_name_1, record.partner_id.cv_last_name_2) + ' - ' + record.end_date.strftime(
                '%Y%m%d')

    def action_aprobado_cgn(self):
        employee_id = self.env['hr.employee'].sudo().search(
            [('cv_emissor_country_id', '=', self.cv_emissor_country_id.id),
             ('cv_document_type_id', '=', self.cv_document_type_id.id),
             ('cv_nro_doc', '=', self.partner_id.cv_nro_doc)])

        count = self.env['hr.contract'].sudo().search_count([('employee_id', '=', employee_id.id),
                                                             ('legajo_state', '=', 'active')])
        if count == len(self.employment_relationship_ids.filtered(lambda x: x.selected)):
            CvDigital = self.env['onsc.cv.digital']
            cv_digital = CvDigital.suspend_security().search(
                [('cv_emissor_country_id', '=', self.cv_emissor_country_id.id),
                 ('cv_document_type_id', '=', self.cv_document_type_id.id),
                 ('cv_nro_doc', '=', self.partner_id.cv_nro_doc),
                 ('type', '=', 'cv')], limit=1)
            cv_digital.suspend_security().write({'is_docket_active': False})

        for vl in self.employment_relationship_ids.filtered(lambda x: x.selected):
            contrato_id = self.env['hr.contract'].sudo().browse(vl.contract_id.id)
            data = {
                'id_deregistration_discharge': self.id_baja,
                'reason_deregistration': self.reason_description or False,
                'norm_code_deregistration_id': self.norm_id and self.norm_id.id or False,
                'type_norm_deregistration': self.norm_type or False,
                'norm_number_deregistration': self.norm_number or False,
                'norm_year_deregistration': self.norm_year or False,
                'norm_article_deregistration': self.norm_article or False,
                'resolution_description_deregistration': self.resolution_description or False,
                'resolution_date_deregistration': self.resolution_date or False,
                'resolution_type_deregistration': self.resolution_type or False,
                'causes_discharge_id': self.causes_discharge_id and self.causes_discharge_id.id or False,
                'additional_information_deregistration': self.additional_information,
                'legajo_state': 'baja',
                'causes_discharge_extended': self.causes_discharge_extended_id and self.causes_discharge_extended_id.id or False
            }

            for attach in self.attached_document_discharge_ids:
                attach.write({
                    'contract_id': contrato_id.id,
                    'type': 'deregistration'})

            contrato_id.suspend_security().write(data)
            vl.job_id.write({'end_date': self.end_date})

        self.write({'state': 'aprobado_cgn'})

        return True

    def action_rechazado_cgn(self):
        self.write({'state': 'rechazado_cgn'})
        return True
