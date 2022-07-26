# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ONSCCVEntry(models.Model):
    _name = 'onsc.cv.entry'
    _description = 'Rubro'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del rubro", required=True, tracking=True)
