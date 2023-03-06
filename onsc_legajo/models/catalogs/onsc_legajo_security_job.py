# -*- coding: utf-8 -*-
import json

from odoo import fields, models


class ONSCLegajoSecurityJob(models.Model):
    _name = 'onsc.legajo.security.job'
    _description = 'Seguridad de puesto'

    name = fields.Char(string='Nombre de la seguridad de puesto', required=True)
    is_uo_manager = fields.Boolean(string='Es responsable UO')
    user_role_ids = fields.Many2many('res.users.role', string='Roles', required=True)
    active = fields.Boolean('Activo', default=True)
    user_role_ids_domain = fields.Char(default=lambda self: self._user_role_ids_domain(),
                                       compute='_compute_user_role_ids_domain')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la seguridad de puesto debe ser única'),
    ]

    def _compute_user_role_ids_domain(self):
        for rec in self:
            rec.user_role_ids_domain = self._user_role_ids_domain()

    def write(self, vals):
        res = super(ONSCLegajoSecurityJob, self).write(vals)
        if vals.get('user_role_ids'):
            self.update_jobs_security()
        return res

    def _user_role_ids_domain(self):
        return json.dumps([('id', 'not in', self.env.ref('base.default_user').with_context(active_test=False).role_line_ids.mapped('role_id').ids)])

    def update_jobs_security(self):
        Job = self.env['hr.job']
        for record in self:
            jobs = Job.search([('security_job_id', '=',record.id)])
            for job in jobs.filtered(lambda x: x.is_roles_duplicated(record.user_role_ids) is False):
                new_lines = [(5,)]
                for user_role_id in record.user_role_ids:
                    new_lines.append((0, 0, {
                        'user_role_id': user_role_id.id,
                        'type': 'system',
                        'start_date': job.start_date if job.start_date else fields.Date.today(),
                        'end_date': job.end_date
                    }))
                job.write({
                    'role_ids': new_lines
                })
