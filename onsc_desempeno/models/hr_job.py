# -*- coding: utf-8 -*-

from odoo import models, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    @api.model
    def create(self, vals):
        record = super(HrJob, self).create(vals)
        return record
