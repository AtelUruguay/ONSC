# -*- coding: utf-8 -*-
from odoo import models
from odoo import Command


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.volunteering'
    _legajo_model = 'onsc.legajo.volunteering'

    def _update_legajo_record_vals(self, vals):
        if 'volunteering_task_ids' in vals:
            vals['volunteering_task_ids'] = [Command.clear()] + vals['volunteering_task_ids']
        return vals
