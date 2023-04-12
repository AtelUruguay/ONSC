# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ONSCLegajoAltaVLAttachedDocument(models.Model):
    _name = 'onsc.legajo.alta.vl.attached.document'
    _description = 'Documentos adjuntos en Alta VL'

    name = fields.Char('Descripción')
    document_type_id = fields.Many2one('onsc.legajo.document.type', 'Tipo de documento')
    document_file = fields.Binary('Archivo')
    document_file_name = fields.Char('Nombre del archivo')
    alta_vl_id = fields.Many2one('onsc.legajo.alta.vl', 'Alta VL')

    @api.constrains('document_file_name')
    def _check_file(self):
        if str(self.document_file_name.split(".")[1]) != 'pdf':
            raise ValidationError("No puede adjuntar archivos diferentes de .pdf")

