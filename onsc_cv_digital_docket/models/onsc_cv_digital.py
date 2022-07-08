# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigital(models.Model):
    _inherit = 'onsc.cv.digital'

    is_docket = fields.Boolean(string="Tiene legajo")
    gender_date = fields.Date(string="Fecha de información Género")
    gender_public_visualization_date = fields.Date(string="Fecha información visualización pública de género")
    afro_descendant_date = fields.Date(string="Fecha de información afrodescendencia")
    status_civil_date = fields.Date(string="Fecha de información stado civil")
