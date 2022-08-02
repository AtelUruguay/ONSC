# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    address_info_date = fields.Date(string="Fecha de información domicilio")
    address_receipt_file = fields.Binary('Constancia de domicilio')
    address_receipt_file_name = fields.Char('Nombre del fichero de constancia de domicilio')
