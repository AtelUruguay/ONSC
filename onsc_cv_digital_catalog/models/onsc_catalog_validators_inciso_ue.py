# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ONSCCatalogValidatorsIncisoUE(models.Model):
    _name = 'onsc.catalog.validators.inciso.ue'
    _description = 'Validadores por Inciso y UE'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True, ondelete='restrict',
                                history=True, index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        ondelete='restrict',
                                        history=True)
    user_id = fields.Many2one('res.users', 'Usuario',history=True)
    security = fields.Char(string="Seguridad", compute='_compute_security')
    active = fields.Boolean(default=True, history=True)

    def _compute_security(self):
        for record in self:
            validator = self.env['ir.config_parameter'].sudo().get_param("Validador documental llamados", False)
            record.security = validator if validator else ""

    @api.constrains('inciso_id', 'operating_unit_id','user_id')
    def _check_valid(self):
        for record in self:
            if not record.personal_phone and not record.mobile_phone:
                raise ValidationError(_("Ya existe un usuario configurado para ese Inciso y UE"))