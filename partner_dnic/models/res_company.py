# -*- coding: utf-8 -*-

from odoo import fields, models

DNIC_DOC_TYPE = [
    ('DO', 'DO')
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_dnic_integrated = fields.Boolean(u'Integración con DNIC')
    dnic_wsdl = fields.Char('URL del WSDL(DNIC)')
    dnic_organization = fields.Char(u'Organización(DNIC)')
    dnic_password = fields.Char(u'Contraseña entidad(DNIC)')
    dnic_doc_type = fields.Selection(DNIC_DOC_TYPE, u'Tipo de documento(DNIC)')
