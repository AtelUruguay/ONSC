# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalGeneralInfo(models.Model):
    _name = 'onsc.cv.digital.general.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Currículum digital: información gdneral'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", required=True, )
