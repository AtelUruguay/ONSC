# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCLegajoAttachedDocument(models.Model):
    _name = 'onsc.legajo.attached.document'
    _description = 'Documentos adjuntos'

    name = fields.Char('Descripción')
    document_type_id = fields.Many2one('onsc.legajo.document.type', 'Tipo de documento')
    document_file = fields.Binary('Archivo')
    document_file_name = fields.Char('Nombre del archivo')
    type = fields.Selection([('deregistration', 'Baja'), ('discharge', 'Alta')], 'Tipo')
    contract_id = fields.Many2one('hr.contract', 'Contrato', ondelete='cascade')
    alta_vl_id = fields.Many2one('onsc.legajo.alta.vl', 'Alta VL', ondelete='cascade')
    baja_vl_id = fields.Many2one("onsc.legajo.baja.vl", string="Baja de vínculo laboral", ondelete='cascade')
    alta_cs_id = fields.Many2one('onsc.legajo.alta.cs', 'Alta CS', ondelete='cascade')
    baja_cs_id = fields.Many2one("onsc.legajo.baja.cs", string="Baja de vínculo laboral", ondelete='cascade')
    cambio_uo_id = fields.Many2one("onsc.legajo.cambio.uo", string="Cambio UO", ondelete='cascade')

    @api.constrains('document_file_name')
    def _check_document_file_name(self):
        for record in self.filtered(lambda x: x.document_file):
            if not record.document_file_name:
                raise ValidationError(_("El archivo es incorrecto"))
            else:
                tmp = self.document_file_name.split('.')
                ext = tmp[len(tmp) - 1]
                if ext != 'pdf':
                    raise ValidationError(_("El archivo debe ser un pdf"))
