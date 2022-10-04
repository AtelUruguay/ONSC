# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCatalogValidatorsIncisoUE(models.Model):
    _name = 'onsc.catalog.validators.inciso.ue'
    _description = 'Validadores por Inciso y UE'
    _rec_name = 'user_id'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True, ondelete='restrict')
    company_id = fields.Many2one('res.company',
                                 related='inciso_id.company_id',
                                 store=True,
                                 ondelete='restrict')
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        required=True,
                                        ondelete='restrict')
    user_id = fields.Many2one('res.users',
                              string='Usuario',
                              required=True, )
    group_id = fields.Many2one('res.groups',
                               string='Seguridad',
                               default=lambda self: self.get_default_group_id())

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        self.operating_unit_id = False

    @api.model
    def get_default_group_id(self):
        security_param = self.env['ir.config_parameter'].sudo().get_param("group_documentary_validator", "")
        return self.env['res.groups'].search([('name', '=', security_param)]).id

    @api.constrains('inciso_id', 'operating_unit_id', 'user_id')
    def _check_valid(self):
        for record in self:
            if record.inciso_id and record.operating_unit_id and record.user_id and self.search_count(
                    [('inciso_id', '=', record.inciso_id.id), ('operating_unit_id', '=', record.operating_unit_id.id),
                     ('user_id', '=', record.user_id.id), ('id', '!=', record.id)]):
                raise ValidationError(_("Ya existe un usuario configurado para ese Inciso y UE"))

    @api.model
    def create(self, values):
        new_recordset = super(ONSCCatalogValidatorsIncisoUE, self).create(values)
        user_seg = self.search_count([("user_id", "=", self.user_id.id)])
        if user_seg == 1:
            if new_recordset.user_id.id not in new_recordset.group_id.users.ids:
                new_recordset.user_id.suspend_security().write({
                    'groups_id': [(4, new_recordset.group_id.id)]
                })
        return new_recordset

    def write(self, values):
        user_id = values.get('user_id')
        user_seg = self.search_count([("user_id", "=", self.user_id.id)])
        if user_seg == 1:
            if user_id:
                for record in self:
                    record.user_id.suspend_security().write({'groups_id': [(3, record.group_id.id)]})
        recordsets = super(ONSCCatalogValidatorsIncisoUE, self).write(values)
        if user_seg == 1:
            if user_id:
                record.mapped('user_id').suspend_security().write({'groups_id': [(4, user_id)]})
        return recordsets

    def unlink(self):
        user_seg = self.search_count([("user_id", "=", self.user_id.id)])
        if user_seg == 1:
            for record in self:
                record.user_id.suspend_security().write({'groups_id': [(3, record.group_id.id)]})
        return super(ONSCCatalogValidatorsIncisoUE, self).unlink()
