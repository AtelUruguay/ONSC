# -*- coding: utf-8 -*-
import json

from odoo import fields, models


class HrJobRoleLine(models.Model):
    _inherit = 'hr.job.role.line'

    user_role_id_domain = fields.Char(default=lambda self: self._user_role_id_domain(),
                                      compute='_compute_user_role_id_domain')

    def _compute_user_role_id_domain(self):
        for rec in self:
            rec.user_role_id_domain = self._user_role_id_domain()

    def _user_role_id_domain(self):
        if self.user_has_groups(
                'onsc_legajo.group_legajo_configurador_puesto_ajuste_seguridad_manual_informatica_onsc'):
            args = [('rol_type', 'in', [False, 'config_onsc'])]
        else:
            args = [('rol_type', '=', False)]
        roles = self.env['res.users.role'].search(args)
        return json.dumps([('id', 'in', roles.ids)])
