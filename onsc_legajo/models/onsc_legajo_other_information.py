# -*- coding: utf-8 -*-

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCLegajoOtherInformation(models.Model):
    _name = "onsc.legajo.other.information"
    _description = 'Otra información de funcionario'

    entry_date = fields.Date(
        string="Fecha de ingreso de información",
        required=True,
        default=lambda s: fields.Date.today())
    title = fields.Char(string="Título", required=True)
    description = fields.Char(string="Descripción", required=True)
    digital_file = fields.Binary(string="Documento digitalizado", required=True)
    digital_filename = fields.Char("Nombre del documento digitalizado")
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", required=True)

    @api.constrains("entry_date")
    def _check_date(self):
        for record in self:
            if record.entry_date > fields.Date.today():
                raise ValidationError(_("La Fecha de ingreso de información debe ser menor o igual al día de hoy"))

    @api.onchange('entry_date')
    def onchange_date(self):
        if self.entry_date and self.entry_date > fields.Date.today():
            self.entry_date = False
            return warning_response(_(u"La Fecha de ingreso de información debe ser menor o igual al día de hoy"))
