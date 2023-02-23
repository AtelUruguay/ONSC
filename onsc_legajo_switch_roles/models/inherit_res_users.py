# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUser(models.Model):
    _inherit = "res.users"

    def change_job(self, jobId):
        super(ResUser, self).change_job(jobId=jobId)
        self.env.user.set_roles(jobId)

    def set_roles(self, jobId=False):
        for rec in self:
            list_users = self.env['res.users']
            list_users |= self.env.ref('base.user_admin')
            list_users |= self.env.ref('base.default_user')
            list_users |= self.env.ref('base.public_user')
            if rec not in list_users and jobId:
                rol_list = self.env['res.users.role'].sudo()
                role_line_ids = [(5, 0, 0)]

                default_roles = self.env['res.users.role'].sudo().search([('rol_type', '=', 'default')])
                for role in default_roles:
                    vals = {
                        'role_id': role.id,
                        'is_enabled': True
                    }
                    role_line_ids.append((0, 0, vals))
                    rol_list |= role

                job_id = self.env['hr.job'].sudo().browse(jobId)
                for role in job_id.role_ids:
                    if role.user_role_id not in rol_list:
                        vals = {
                            'role_id': role.user_role_id.id,
                            'date_from': role.start_date,
                            'date_to': role.end_date,
                            'is_enabled': True
                        }
                        role_line_ids.append((0, 0, vals))
                        rol_list |= role.user_role_id

                for role in job_id.role_extra_ids:
                    if role.user_role_id not in rol_list:
                        vals = {
                            'role_id': role.user_role_id.id,
                            'date_from': role.start_date,
                            'date_to': role.end_date,
                            'is_enabled': True
                        }
                        role_line_ids.append((0, 0, vals))
                        rol_list |= role.user_role_id

                rec.sudo().write(
                    {
                        'role_line_ids': role_line_ids
                    }
                )

    def reset_roles(self):
        list_users = self.env['res.users']
        list_users |= self.env.ref('base.user_admin')
        list_users |= self.env.ref('base.default_user')
        list_users |= self.env.ref('base.public_user')
        for rec in self:
            rec = rec.sudo()
            if rec not in list_users:
                if rec.employee_id:
                    rec.employee_id.job_id = False
                role_line_ids = []
                role_lines = []

                default_roles = self.env['res.users.role'].sudo().search([('rol_type', '=', 'default')])
                for role in default_roles:
                    lines = self.env['res.users.role.line'].sudo().search(
                        [
                            ('active', 'in', [False, True]),
                            ('user_id', '=', rec.id),
                            ('role_id', '=', role.id)
                        ]
                    )
                    if lines:
                        for line in lines:
                            line.sudo().write(dict(active=True))
                            role_lines.append(line.id)
                    else:
                        vals = {
                            'role_id': role.id,
                            'user_id': rec.id,
                            'is_enabled': True
                        }
                        new_line = self.env['res.users.role.line'].sudo().create(vals)
                        role_lines.append(new_line.id)
                role_line_ids += [(6, 0, role_lines)]
                rec.sudo().write(
                    {
                        'role_line_ids': role_line_ids
                    }
                )
                self.env.cr.commit()
