# pylint: disable=E8102
# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUser(models.Model):
    _inherit = "res.users"

    def change_job(self, jobId):
        super(ResUser, self).change_job(jobId=jobId)
        self.env.user.set_roles(jobId)

    def get_jobs_domain(self):
        today = fields.Date.to_string(fields.Date.today())
        domain = [
            '&', '&', ('start_date', '<=', today),
            '|', ('end_date', '>=', today), ('end_date', '=', False),
            '|', ('employee_id', '=', False), ('employee_id', '=', self.employee_id.id)]
        return domain

    def filter_job_role_lines(self, job_role_lines):
        today = fields.Date.today()
        return job_role_lines.filtered(
            lambda x: x.start_date <= today and ((x.end_date and x.end_date >= today) or not x.end_date))

    def _prepare_data(self, role):
        return {
            'role_id': role.user_role_id.id,
            'date_from': role.start_date,
            'date_to': role.end_date,
            'is_enabled': True,
            'is_job_role_line': True
        }

    def set_roles(self, jobId=False):
        if jobId is False:
            return
        list_users = self.env['res.users']
        list_users |= self.env.ref('base.user_admin')
        list_users |= self.env.ref('base.default_user')
        list_users |= self.env.ref('base.public_user')
        for rec in self.filtered(lambda x: x not in list_users):
            rec.sudo().role_line_ids.filtered(lambda x: x.is_job_role_line).unlink()
            rol_list = self.env['res.users.role'].sudo()
            role_line_ids = []
            job_id = self.env['hr.job'].sudo().browse(jobId)

            _roles = job_id.role_ids
            _roles |= job_id.role_extra_ids
            for role in self.filter_job_role_lines(_roles):
                if role.user_role_id not in rol_list:
                    role_line_ids.append((0, 0, self._prepare_data(role)))
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
            rec._clean_role_lines()
            role_lines = rec.get_roleline_one_job()
            if len(role_lines):
                rec.sudo().write({'role_line_ids': role_lines})
            self.env.cr.commit()

    def _clean_role_lines(self):
        self.role_line_ids.filtered(lambda x: x.is_job_role_line).unlink()


    def get_roleline_one_job(self):
        role_line_ids = []
        domain = self.get_jobs_domain()
        jobs = self.env['hr.job'].sudo().search(domain)
        job_id = jobs[0].id if len(jobs) == 1 else False
        self.employee_id.job_id = job_id
        if len(jobs):
            self.action_id = False
        job_id = self.env['hr.job'].sudo().browse(job_id)
        _roles = job_id.role_ids
        _roles |= job_id.role_extra_ids
        user_role_ids = self.role_line_ids.mapped('role_id').ids
        for role in self.filter_job_role_lines(_roles):
            if role.user_role_id.id not in user_role_ids:
                role_line_ids.append((0, 0, self._prepare_data(role)))
        return role_line_ids
