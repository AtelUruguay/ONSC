# -*- coding: utf-8 -*-

from odoo import fields, models

DNIC_DOC_TYPE = [
    ('DO', 'DO')
]


class ResCompany(models.Model):
    _inherit = 'res.company'



    cv_help_contacts = fields.Char('Contactos')
