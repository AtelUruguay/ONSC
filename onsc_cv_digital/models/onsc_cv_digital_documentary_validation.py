# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalDocumentaryValidation(models.Model):
    _name = 'onsc.cv.documentary.validation'
    _description = 'Modelo generico para validar documentos'

    _inherit = ['onsc.cv.abstract.config']

    validation_date = fields.Date(string="Fecha validación documental")
    validation_user_id = fields.Many2one("res.users", string="Usuario validación documental")


class IrAttachment(models.Model):
    _name = 'ir.attachment'

    _inherit = ['onsc.cv.documentary.validation', 'ir.attachment']
