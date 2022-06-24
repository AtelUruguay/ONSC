# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError

from ..soap import dnic_client

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    general_info_help = fields.Char(related="company_id.general_info_help", readonly=False)
