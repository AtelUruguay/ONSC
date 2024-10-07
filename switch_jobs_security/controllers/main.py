# -*- coding: utf-8 -*-
# pylint: disable=R8180

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        user = request.env.user
        session_info = super(Http, self).session_info()
        domain = user.get_jobs_domain()
        jobs = self.env['hr.job'].sudo().search(domain)
        if jobs:
            session_info.update({
                "jobs": {
                    'current_job': user.employee_id.job_id.id,
                    'jobs': {
                        job.id: {
                            'id': job.id,
                            'name': job.name,
                        } for job in jobs if len(jobs) >= 1
                    },
                }
            })
        return session_info
