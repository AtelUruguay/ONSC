# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalDocumentaryValidation(models.Model):
    _name = 'onsc.cv.digital.documentary.validation'
    _description = 'Modelo generico para validar documentos'

    document_validation_status = fields.Selection(string="Estado validación documental ",
                                                  selection=[('pendiente_validacion', 'Pendiente de validación '),
                                                             ('validado', 'Validado'), ('rechazado', 'Rechazado')],
                                                  default="pendiente_validacion")
    reason_rejection = fields.Char(string="Motivo rechazo validación documental")
    document_validation_date = fields.Date(string="Fecha validación documental ")
    user_validation_documentary_id = fields.Many2one(comodel_name="res.users", string="Usuario validación documental")


class IrAttachment(models.Model):
    _name = 'ir.attachment'

    _inherit = ['onsc.cv.digital.documentary.validation', 'ir.attachment']
