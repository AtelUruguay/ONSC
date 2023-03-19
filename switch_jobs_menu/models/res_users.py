# -*- coding: utf-8 -*-
from odoo import models


class ResUser(models.Model):
    _inherit = "res.users"

    def change_job(self, jobId):
        self.env.user.employee_id.write(dict(job_id=jobId))

    def get_jobs_domain(self):
        domain = []
        return domain
