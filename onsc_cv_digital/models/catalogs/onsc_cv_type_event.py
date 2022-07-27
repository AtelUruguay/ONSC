# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVTypeEvent(models.Model):
    _name = 'onsc.cv.type.event'
    _description = 'Tipo de evento'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(" Nombre del tipo de evento", required=True, tracking=True)
