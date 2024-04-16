# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ONSCLegajoOtherInformation(models.Model):
    _name = "onsc.legajo.other.information"
    _description = 'Otra información de funcionario'

    document_date = fields.Date(string="Fecha de ingreso de información", required=True, default=fields.Date.today)
    title = fields.Text(string="Título", required=True)
    description = fields.Text(string="Descripción", required=True)
    digital_file = fields.Binary(string="Documento digitalizado", required=True)
    digital_filename = fields.Char("Nombre del documento digitalizado")
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", required=True)

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
