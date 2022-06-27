# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cv_help_general_info = fields.Char(related="company_id.cv_help_general_info", readonly=False)
    cv_help_address = fields.Char(related="company_id.cv_help_address", readonly=False)
