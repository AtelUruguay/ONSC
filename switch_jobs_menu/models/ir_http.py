# -*- coding: utf-8 -*-
import odoo
from odoo import api, http, models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def get_domain(self, user):
        domain = []
        return domain

    def session_info(self):
        user = request.env.user
        session_info = super(Http, self).session_info()
        domain = self.get_domain(user)
        jobs = self.env['hr.job'].sudo().search(domain)
        session_info.update({
            "jobs": {
                'current_job': user.employee_id.job_id.id,
                'jobs': {
                    job.id: {
                        'id': job.id,
                        'name': job.name,
                    } for job in jobs
                },
            }
        })
        return session_info
