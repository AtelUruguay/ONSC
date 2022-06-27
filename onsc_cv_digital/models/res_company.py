# -*- coding: utf-8 -*-

from odoo import fields, models

DNIC_DOC_TYPE = [
    ('DO', 'DO')
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    cv_help_general_info = fields.Char('Información General')
    cv_help_address = fields.Char('Domicilio')
