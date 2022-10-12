# -*- coding: utf-8 -*-

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ONSCCVDigitalCall(models.Model):
    _name = 'onsc.cv.digital.call'
    _inherit = 'onsc.cv.digital.call'

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalCall, self)._get_json_dict()
        json_dict.extend(['cv_source_info_auth_type'])
        return json_dict
