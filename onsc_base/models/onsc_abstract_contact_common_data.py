# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCContactCommonData(models.Model):
    _name = 'onsc.contact.common.data'
    _description = 'Modelo abstracto común para los datos personales'

    document_identity_file = fields.Binary(string="Documento digitalizado del documento de identidad")
    document_identity_filename = fields.Char('Nombre del documento digital')


