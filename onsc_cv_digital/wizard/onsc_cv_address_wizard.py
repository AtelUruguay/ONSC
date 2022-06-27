# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCCVAddressWizard(models.TransientModel):
    _name = 'onsc.cv.address.wizard'
    _description = 'Crear y editar Domicilios de CV'

    def _default_partner_id(self):
        return self.env['res.partner'].search([('user_ids', 'in', self.env.user.id)], limit=1)

    partner_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        required=True,
        default=_default_partner_id)

    country_id = fields.Many2one(related='partner_id.country_id', readonly=False)
    cv_address_state_id = fields.Many2one(related='partner_id.state_id', readonly=False)
    cv_address_location_id = fields.Many2one(related='partner_id.cv_location_id', readonly=False)
    cv_address_street = fields.Char(related='partner_id.street', readonly=False)
    cv_address_nro_door = fields.Char(related='partner_id.cv_nro_door', readonly=False)
    cv_address_apto = fields.Char(related='partner_id.cv_apto', readonly=False)
    cv_address_street2 = fields.Char(related='partner_id.street2', readonly=False)
    cv_address_street3 = fields.Char(related='partner_id.cv_street3', readonly=False)
    cv_address_zip = fields.Char(related='partner_id.zip', readonly=False)
    cv_address_is_cv_bis = fields.Boolean(related='partner_id.is_cv_bis', readonly=False)
    cv_address_amplification = fields.Text(related='partner_id.cv_amplification', readonly=False)

    def action_address(self):
        "Esta acción no requiere implementación porque al guardar se reflejan los valores en el partner"
