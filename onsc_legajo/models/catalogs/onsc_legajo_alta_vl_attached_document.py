# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCLegajoAltaVLAttachedDocument(models.Model):
    _name = 'onsc.legajo.alta.vl.attached.document'
    _description = 'Documentos adjuntos en Alta VL'

    name = fields.Char('Descripción')
    document_type_id = fields.Many2one('onsc.legajo.document.type', 'Tipo de documento')
    document_file = fields.Binary('Archivo')
    document_file_name = fields.Char('Nombre del archivo')
    alta_vl_id = fields.Many2one('onsc.legajo.alta.vl', 'Alta VL')
