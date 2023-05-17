# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.experience'

    causes_discharge = fields.Char(string=u"Causal de egreso")
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string=u"Causal de egreso")

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalWorkExperience, self)._get_json_dict()
        json_dict.extend([
            ("causes_discharge"),
        ])
        return json_dict
