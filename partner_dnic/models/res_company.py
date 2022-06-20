# -*- coding: utf-8 -*-

from odoo import fields, models

DNIC_DOC_TYPE = [
    ('DO', 'DO')
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_dnic_integrated = fields.Boolean(u'Integración con DNIC')
    dnic_wsdl = fields.Char('URL del WSDL')
    dnic_organization = fields.Char(u'Organización')
    dnic_password = fields.Char(u'Contraseña entidad')
    dnic_doc_type = fields.Selection(DNIC_DOC_TYPE, u'Tipo de documento')
