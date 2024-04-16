# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ONSCLegajoDemerito(models.Model):
    _name = "onsc.legajo.demerito"
    _description = 'Demérito'

    demerit_id = fields.Many2one(comodel_name="onsc.legajo.type.demerit", string="Tipo de demérito", required=True, )
    title = fields.Text(string="Título", required=True)
    inciso_id = fields.Many2one(comodel_name="onsc.catalog.inciso", string="Inciso", required=True)
    operating_unit_id = fields.Many2one(comodel_name="operating.unit", string="Unidad ejecutora", required=True)
    document_date = fields.Date(string="Fecha del documento", required=True)
    digital_file = fields.Binary(string="Documento digitalizado", required=True)
    digital_filename = fields.Char("Nombre del documento digitalizado", required=True)
    notification_date = fields.Date(string="Fecha de notificación", required=True)
    start_date = fields.Date(string="Fecha inicio", required=True)
    end_date = fields.Date(string="Fecha hasta", required=True)
    description = fields.Text(string="Descripción del demérito", required=True)
    type_sanction_id = fields.Many2one(comodel_name="onsc.legajo.type.sanction", string="Tipo de sanción",
                                       required=True, )
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", required=True)

    @api.constrains("document_date")
    def _check_document_date(self):
        for record in self:
            if record.document_date > fields.Date.today():
                raise ValidationError("La fecha del documento debe ser menor o igual al día de hoy")

    @api.constrains("notification_date")
    def _check_notification_date(self):
        for record in self:
            if record.notification_date > fields.Date.today():
                raise ValidationError("La fecha de notificación debe ser menor o igual al día de hoy")

    @api.onchange('document_date')
    def onchange_document_date(self):
        if self.document_date and self.document_date > fields.Date.today():
            self.document_date = False
            return warning_response(_(u"La Fecha de documento debe ser menor o igual al día de hoy"))

    @api.onchange("notification_date")
    def onchange_notification_date(self):
        if self.notification_date and self.notification_date > fields.Date.today():
            self.notification_date = False
            return warning_response(_(u"La fecha de notificación debe ser menor o igual al día de hoy"))

    @api.onchange("inciso_id")
    def onchange_inciso_id(self):
        self.operating_unit_id = False

    @api.onchange("demerit_id")
    def onchange_demerit_id(self):
        if self.type_sanction_id:
            self.type_sanction_id = False
        if self.description:
            self.description = False

    @api.onchange('type_sanction_id')
    def onchange_type_sanction_id(self):
        if self.type_sanction_id:
            self.description = self.type_sanction_id.summary
