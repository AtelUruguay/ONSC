# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVSettings(models.TransientModel):
    _name = "onsc.cv.settings"
    _inherit = ['onsc.cv.settings']
    _description = u"Configuración"

    cv_help_contacts = fields.Char(related="company_id.cv_help_contacts", readonly=False, related_sudo=True)
