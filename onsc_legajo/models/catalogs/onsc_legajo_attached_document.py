# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCLegajoAttachedDocument(models.Model):
    _name = 'onsc.legajo.attached.document'
    _description = 'Documentos adjuntos'

    name = fields.Char('Descripción')
    document_type_id = fields.Many2one('onsc.legajo.document.type', 'Tipo de documento')
    document_file = fields.Binary('Archivo')
    document_file_name = fields.Char('Nombre del archivo')
    type = fields.Selection([('deregistration', 'Baja'), ('discharge', 'Alta')], 'Tipo')
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    alta_vl_id = fields.Many2one('onsc.legajo.alta.vl', 'Alta VL')
    baja_vl_id = fields.Many2one("onsc.legajo.baja.vl", string="Baja de vínculo laboral")
    baja_cs_id = fields.Many2one("onsc.legajo.baja.cs", string="Baja de vínculo laboral")
