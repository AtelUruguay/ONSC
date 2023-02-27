# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUser(models.Model):
    _inherit = "res.users"

    def change_job(self, jobId):
        super(ResUser, self).change_job(jobId=jobId)
        self.env.user.set_roles(jobId)

    def set_roles(self, jobId=False):
        if jobId is False:
            return
        list_users = self.env['res.users']
        list_users |= self.env.ref('base.user_admin')
        list_users |= self.env.ref('base.default_user')
        list_users |= self.env.ref('base.public_user')
        for rec in self.filtered(lambda x: x not in list_users):
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
            _roles = job_id.role_ids
            _roles |= job_id.role_extra_ids
            for role in _roles:
                if role.user_role_id not in rol_list:
                    vals = {
                        'role_id': role.user_role_id.id,
                        'date_from': role.start_date,
                        'date_to': role.end_date,
                        'is_enabled': True
                    }
                    role_line_ids.append((0, 0, vals))
                    rol_list |= role.user_role_id

            rec.sudo().write({
                'role_line_ids': role_line_ids
            })

    def reset_roles(self):
        list_users = self.env['res.users']
        list_users |= self.env.ref('base.user_admin')
        list_users |= self.env.ref('base.default_user')
        list_users |= self.env.ref('base.public_user')
        for rec in self.filtered(lambda x: x not in list_users):
            rec = rec.sudo()
            role_line_ids = []
            role_lines = []
            rol_list = self.env['res.users.role'].sudo()

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
                        if role not in rol_list:
                            line.sudo().write(dict(active=True))
                            role_lines.append(line.id)
                            rol_list |= role
                else:
                    vals = {
                        'role_id': role.id,
                        'user_id': rec.id,
                        'is_enabled': True
                    }
                    new_line = self.env['res.users.role.line'].sudo().create(vals)
                    role_lines.append(new_line.id)
                    rol_list |= role

            role_line_ids += [(6, 0, role_lines)]
            role_line_ids = self.get_roleline_one_job(role_line_ids, rol_list)
            rec.sudo().write(
                {
                    'role_line_ids': role_line_ids
                }
            )
            self.env.cr.commit()

    def get_jobs_domain(self):
        today = fields.Date.today()
        domain = [
            '&', '&', ('start_date', '<=', fields.Date.to_string(today)),
            '|', ('end_date', '>=', fields.Date.to_string(today)), ('end_date', '=', False),
            '|', ('employee_id', '=', False), ('employee_id', '=', self.employee_id.id)]
        return domain

    def get_roleline_one_job(self, role_line_ids, rol_list):
        domain = self.get_jobs_domain()
        jobs = self.env['hr.job'].sudo().search(domain)
        job_id = jobs[0].id if len(jobs) == 1 else False
        self.employee_id.job_id = job_id

        job_id = self.env['hr.job'].sudo().browse(job_id)
        _roles = job_id.role_ids
        _roles |= job_id.role_extra_ids
        for role in _roles:
            if role.user_role_id not in rol_list:
                vals = {
                    'role_id': role.user_role_id.id,
                    'date_from': role.start_date,
                    'date_to': role.end_date,
                    'is_enabled': True
                }
                role_line_ids.append((0, 0, vals))
                rol_list |= role.user_role_id
        return role_line_ids

