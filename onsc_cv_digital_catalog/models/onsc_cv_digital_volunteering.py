# -*- coding: utf-8 -*-
from odoo import models


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _inherit = 'onsc.cv.volunteering'

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalVolunteering, self)._get_json_dict()
        json_dict.extend([
            ("inciso_id", ['id', 'name']),
            ("operating_unit_id", ['id', 'name']),
        ])
        return json_dict
