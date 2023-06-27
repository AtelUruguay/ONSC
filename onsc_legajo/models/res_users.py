# -*- coding: utf-8 -*-

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _clean_role_lines(self):
        default_user_role_ids = self.env.ref('base.default_user').with_context(
            active_test=False).role_line_ids.mapped('role_id').ids
        if self.employee_id and self.employee_id.legajo_state == 'egresed':
            role_lines = self.role_line_ids.filtered(
                lambda x: x.is_job_role_line or x.role_id.id not in default_user_role_ids)
        else:
            role_lines = self.role_line_ids.filtered(lambda x: x.is_job_role_line)
        role_lines.unlink()
