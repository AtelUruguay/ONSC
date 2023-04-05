# -*- coding: utf-8 -*-

import json

from odoo import fields, models, api


class ONSCCVFileValidationConfig(models.Model):
    _inherit = 'onsc.cv.documentary.validation.config'

    state = fields.Selection(string="",
                             selection=[('cv_call', 'Llamado'),
                                        ('legajo', 'Legajo')
                                        ('both', 'Ambos')],
                             required=False, )