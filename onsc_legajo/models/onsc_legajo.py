# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class ONSCLegajo(models.Model):
    _inherit = 'onsc.legajo'

