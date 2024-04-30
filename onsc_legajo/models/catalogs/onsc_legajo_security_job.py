# -*- coding: utf-8 -*-
import logging
import json

_logger = logging.getLogger(__name__)

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
    sequence = fields.Integer(string="Nivel", default=1)

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
        return json.dumps([('id', 'not in',
                            self.env.ref('base.default_user').with_context(active_test=False).role_line_ids.mapped(
                                'role_id').ids)])

    def update_jobs_security(self):
        Job = self.env['hr.job']
        JobLine = self.env['hr.job.role.line'].sudo()
            # new_lines = []
            # for user_role_id in record.user_role_ids:
            #     new_lines.append({
            #         'user_role_id': user_role_id.id,
            #         'type': 'system',
            #         # 'start_date': job.start_date if job.start_date else fields.Date.today(),
            #         # 'end_date': job.end_date
            #     }))

        try:
            for record in self:
                _logger.warning('******************1')
                today = fields.Date.today()
                jobs = Job.search([
                    ('security_job_id', '=', record.id),
                    '|', ('end_date', '>=', today), ('end_date', '=', False),
                ])
                _logger.warning('******************1.1 INICIANDO BURBUJA')
                new_lines = []
                for user_role_id in record.user_role_ids:
                    for job in jobs:
                        new_lines.append({
                            'job_id': job.id,
                            'user_role_id': user_role_id.id,
                            'type': 'system',
                            'start_date': job.start_date if job.start_date else fields.Date.today(),
                            'end_date': job.end_date
                        })
                _logger.warning('******************2 LIMPIANDO LINEAS')
                sql_query = """DELETE FROM hr_job_role_line WHERE hr_job_role_line.type='system' AND job_id IN %s"""
                self.env.cr.execute(sql_query, [tuple(jobs.ids)])
                _logger.warning('******************2.1 BULKED CREATION')
                JobLine.create(new_lines)
                # jobs.write({'role_ids': new_lines})
                _logger.warning('******************3 FINALIZANDO ACTUALIZACION DE JOBS')
    #             sql_query = """UPDATE hr_job_role_line
    # SET
    #     start_date = (SELECT start_date FROM hr_job WHERE id = hr_job_role_line.job_id),
    #     end_date = (SELECT end_date FROM hr_job WHERE id = hr_job_role_line.job_id)
    # WHERE
    #     hr_job_role_line.type='system' AND
    #     job_id IN %s"""
    #             self.env.cr.execute(sql_query, [tuple(jobs.ids)])
                _logger.warning('******************4 FIN SQL')
        except Exception as e:
            pass
