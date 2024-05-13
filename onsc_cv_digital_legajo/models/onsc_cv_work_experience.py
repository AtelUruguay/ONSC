# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo import Command


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.experience'
    _legajo_model = 'onsc.legajo.work.experience'

    causes_discharge = fields.Char(string=u"Causal de egreso")
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string=u"Causal de egreso")

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalWorkExperience, self)._get_json_dict()
        json_dict.extend([
            ("causes_discharge"),
        ])
        return json_dict
    def _update_legajo_record_vals(self, vals):
        if 'task_ids' in vals:
            vals['task_ids'] = [Command.clear()] + vals['task_ids']
        return vals
