# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCatalogValidatorsIncisoUE(models.Model):
    _name = 'onsc.catalog.validators.inciso.ue'
    _description = 'Validadores por Inciso y UE'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True, ondelete='restrict', index=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        ondelete='restrict',
                                        history=True)
    user_id = fields.Many2one('res.users', 'Usuario')
    security = fields.Char(string="Seguridad", compute='_compute_security')
    active = fields.Boolean(default=True)

    def _compute_security(self):
        for record in self:
            record.security = self.env['ir.config_parameter'].sudo().get_param("called_document_validator", "")

    @api.constrains('inciso_id', 'operating_unit_id', 'user_id')
    def _check_valid(self):
        for record in self:
            if record.inciso_id and record.operating_unit_id and record.user_id and self.search_count(
                    [('inciso_id', '=', record.inciso_id.id), ('operating_unit_id', '=', record.operating_unit_id.id),
                     ('user_id', '=', record.user_id.id), ('id', '!=', record.id)]):
                raise ValidationError(_("Ya existe un usuario configurado para ese Inciso y UE"))
