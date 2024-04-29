# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoRoleAssignment(models.Model):
    _inherit = 'onsc.legajo.role.assignment'

    def _copy_job_and_create_job_role_assignment(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security().with_context(ignore_security_rules=True)
        Consolidated = self.env['onsc.desempeno.consolidated'].suspend_security().with_context(
            ignore_security_rules=True)

        new_job = super(ONSCLegajoRoleAssignment, self)._copy_job_and_create_job_role_assignment()
        Evaluation.search([
            ('current_job_id', '=', self.job_id.id),
            ('general_cycle_id.active', '=', True),
        ]).write({'current_job_id': new_job.id})
        Evaluation.search([
            ('evaluator_current_job_id', '=', self.job_id.id),
            ('general_cycle_id.active', '=', True),
        ]).write({'evaluator_current_job_id': new_job.id})
        Consolidated.search([
            ('current_job_id', '=', self.job_id.id),
            ('general_cycle_id.active', '=', True),
        ]).write({'current_job_id': new_job.id})
        return new_job
