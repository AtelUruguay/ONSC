# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class ONSCLegajoDeclarationLaw(models.Model):
    _name = "onsc.legajo.declaration.law"
    _description = 'Declaration Law'

    declaration_date = fields.Date(string="Fecha de declaración", required=True)
    digital_file = fields.Binary(string="Documento digitalizado", required=True)
    digital_filename = fields.Char("Nombre del documento digitalizado")
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", required=True)

    @api.constrains("declaration_date")
    def _check_date(self):
        for record in self:
            if record.declaration_date > fields.Date.today():
                raise ValidationError(_("La Fecha de declaración debe ser menor o igual al día de hoy"))

    @api.onchange('declaration_date')
    def onchange_declaration_date(self):
        if self.declaration_date and self.declaration_date > fields.Date.today():
            self.declaration_date = False
            return warning_response(_(u"La Fecha de declaración debe ser menor o igual al día de hoy"))
