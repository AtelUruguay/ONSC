# -*- coding: utf-8 -*-
import json
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCLegajoSecurityJob(models.Model):
    _name = 'onsc.legajo.security.job'
    _description = 'Seguridad de puesto'

    name = fields.Char(string='Nombre de la seguridad de puesto', required=True)
    # is_uo_manager = fields.Boolean(string='Es responsable UO')
    user_role_ids = fields.Many2many('res.users.role', string='Roles', required=True)
    active = fields.Boolean('Activo', default=True)
    user_role_ids_domain = fields.Char(default=lambda self: self._user_role_ids_domain(),
                                       compute='_compute_user_role_ids_domain')
    sequence = fields.Integer(string="Nivel", compute='_compute_sequence', store=True)
    is_default_mass_change_uo = fields.Boolean(string='Seguridad por defecto para el cambio de UO')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la seguridad de puesto debe ser única'),
    ]

    def _compute_user_role_ids_domain(self):
        for rec in self:
            rec.user_role_ids_domain = self._user_role_ids_domain()

    @api.constrains('is_default_mass_change_uo')
    def _constrains_is_default_mass_change_uo(self):
        for rec in self:
            if rec.is_default_mass_change_uo and self.search_count([('is_default_mass_change_uo', '=', True)]) > 1:
                raise ValueError('Solo puede haber una seguridad de puesto por defecto para el cambio de UO')

    @api.depends('user_role_ids')
    def _compute_sequence(self):
        for rec in self:
            rec.sequence = rec.user_role_ids and rec.user_role_ids.sorted(
                key=lambda role: role.sequence)[0].sequence

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
        try:
            for record in self:
                with self._cr.savepoint():
                    _logger.warning('ACTUALIZANDO SEGURIDAD PUESTO')
                    today = fields.Date.today()
                    jobs = Job.search([
                        ('security_job_id', '=', record.id),
                        '|', ('end_date', '>=', today), ('end_date', '=', False),
                    ])
                    _logger.warning('ACTUALIZANDO SEGURIDAD PUESTO LIMPIANDO LINEAS')
                    sql_query = """DELETE FROM hr_job_role_line WHERE hr_job_role_line.type='system' AND job_id IN %s"""
                    self.env.cr.execute(sql_query, [tuple(jobs.ids)])
                    sql_query = """DELETE FROM hr_job_role_line WHERE hr_job_role_line.type='manual' AND job_id IN %s AND user_role_id IN %s"""
                    self.env.cr.execute(sql_query, [tuple(jobs.ids), tuple(record.user_role_ids.ids)])
                    _logger.warning('ACTUALIZANDO SEGURIDAD PUESTO INICIANDO BURBLE')
                    for user_role_id in record.user_role_ids:
                        new_lines = []
                        counter = 0
                        for job in jobs:
                            new_lines.append({
                                'job_id': job.id,
                                'user_role_id': user_role_id.id,
                                'type': 'system',
                                'start_date': job.start_date if job.start_date else fields.Date.today(),
                                'end_date': job.end_date
                            })
                            counter += 1
                        _logger.warning('ACTUALIZANDO SEGURIDAD PUESTO BULKED CREATION %s' % (counter))
                        JobLine.with_context(bulked_creation=True).create(new_lines)
                    # jobs.write({'role_ids': new_lines})
                    _logger.warning('ACTUALIZANDO SEGURIDAD PUESTO FINALIZANDO')
        except Exception:
            pass
