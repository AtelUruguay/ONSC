# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ONSCLegajoJudicialAntecedents(models.Model):
    _name = "onsc.legajo.judicial.antecedents"
    _description = 'Antecedentes Judiciales'

    document_date = fields.Date(string="Fecha del documento")
    digital_file = fields.Binary(string="Documento digitalizado")
    digital_filename = fields.Char("Nombre del documento digitalizado")
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo")
    alta_vl_id = fields.Many2one(comodel_name="onsc.legajo.alta.vl", string="Alta vínculo laboral")

    @api.constrains("document_date")
    def _check_date(self):
        for record in self:
            if record.document_date > fields.Date.today():
                raise ValidationError("La Fecha del documento debe ser menor o igual al día de hoy")
