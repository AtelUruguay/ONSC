# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVRejectWizard(models.TransientModel):
    _name = 'onsc.cv.reject.wizard'
    _description = 'Rechazo de Validación'

    reject_reason = fields.Char(string=u'Motivo de rechazo', required=True)
    model_name = fields.Char(string='Modelo relacionado')
    res_id = fields.Integer("Id del registro relacionado")

    def action_reject(self):
        record = self.env[self.model_name].browse(self.res_id)
        record.sudo()._send_reject_email()
        record.write({'state': 'rejected', 'reject_reason': self.reject_reason})
