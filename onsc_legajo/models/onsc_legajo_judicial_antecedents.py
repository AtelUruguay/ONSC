# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


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

    @api.onchange('document_date')
    def onchange_date(self):
        if self.document_date and self.document_date > fields.Date.today():
            self.document_date = False
            return warning_response(_(u"La Fecha de documento debe ser menor o igual al día de hoy"))
