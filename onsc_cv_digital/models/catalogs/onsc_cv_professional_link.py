# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ONSCCVProfessionalLink(models.Model):
    _name = 'onsc.cv.professional.link'
    _description = 'Vínculo profesional'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre del vínculo profesional", required=True, tracking=True)
