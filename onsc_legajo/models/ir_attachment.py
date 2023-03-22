# -*- coding: utf-8 -*-
from odoo import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    name_field = fields.Char('Nombre del campo histórico')
