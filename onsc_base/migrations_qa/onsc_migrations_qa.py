# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLog(models.Model):
    _name = 'onsc.migrations.qa'
    _description = 'Migraciones manuales a ambientes QA'

    def _v13_0(self):
        # onsc_cv_digital_legajo: 15.0.4.1.0
        for record in self.env['onsc.cv.work.experience'].sudo().search([('causes_discharge_id', '!=', False)]):
            record.causes_discharge = record.causes_discharge_id.name
        # onsc_cv_digital_legajo: 15.0.5.1.2
        self.env['onsc.cv.digital'].sudo().search([('type', '=', 'cv')]).with_context(
            is_legajo=True).button_legajo_update_documentary_validation_sections_tovalidate()
        # onsc_cv_digital 15.0.8.3.6
        for cv in self.env['onsc.cv.digital'].sudo().search([]):
            cv.sudo().write({
                'country_id': cv.partner_id.country_id.id,
                'cv_address_state_id': cv.partner_id.state_id.id,
                'cv_address_location_id': cv.partner_id.cv_location_id.id,
                'cv_address_nro_door': cv.partner_id.cv_nro_door,
                'cv_address_apto': cv.partner_id.cv_apto,
                'cv_address_street': cv.partner_id.street,
                'cv_address_zip': cv.partner_id.zip,
                'cv_address_is_cv_bis': cv.partner_id.is_cv_bis,
                'cv_address_amplification': cv.partner_id.cv_amplification,
                'cv_address_place': cv.partner_id.cv_address_place,
                'cv_address_block': cv.partner_id.cv_address_block,
                'cv_address_sandlot': cv.partner_id.cv_address_sandlot,
            })
