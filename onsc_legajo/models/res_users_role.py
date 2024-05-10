# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResUsersRole(models.Model):
    _inherit = "res.users.role"

    is_byinciso = fields.Boolean(string='Habilitado por inciso')
    is_uo_manager = fields.Boolean(string='¿Es Reponsable UO?')
    sequence = fields.Integer(string="Nivel", default="1")

    @api.constrains("is_uo_manager")
    def _check_unique_is_uo_manager(self):
        for record in self:
            if record.is_uo_manager and self.search_count([('id', '!=', record.id), ('is_uo_manager', '=', True)]):
                raise ValidationError(_("Ya existe otro Rol configurado como Responsable UO."))
