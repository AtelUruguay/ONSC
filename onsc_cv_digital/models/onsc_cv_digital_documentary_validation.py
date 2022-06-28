# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalDocumentaryValidation(models.Model):
    _name = 'onsc.cv.digital.documentary.validation'
    _description = 'Modelo generico para validar documentos'

    validation_status = fields.Selection(string="Estado validación documental",
                                                  selection=[('pendiente_validacion', 'Pendiente de validación '),
                                                             ('validado', 'Validado'), ('rechazado', 'Rechazado')],
                                                  default="pendiente_validacion")
    reject_reason = fields.Char(string="Motivo rechazo validación documental")
    validation_date = fields.Date(string="Fecha validación documental")
    validation_user_id = fields.Many2one("res.users", string="Usuario validación documental")


class IrAttachment(models.Model):
    _name = 'ir.attachment'

    _inherit = ['onsc.cv.digital.documentary.validation', 'ir.attachment']
