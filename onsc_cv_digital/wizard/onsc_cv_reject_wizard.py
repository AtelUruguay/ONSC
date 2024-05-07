# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVRejectWizard(models.TransientModel):
    _name = 'onsc.cv.reject.wizard'
    _description = 'Rechazo de validación'

    reject_reason = fields.Text(string=u'Motivo de rechazo', required=True)
    model_name = fields.Char(string='Modelo relacionado')
    res_id = fields.Integer("Id del registro relacionado")
    res_ids = fields.Many2many("onsc.cv.abstract.config", string="Ids del registro relacionado")
    is_multi = fields.Boolean("Rechazo de multi registros")

    def action_reject(self):
        if self._context.get('is_documentary_reject'):
            return self.action_documentary_reject()
        else:
            return self.action_conditional_reject()

    def action_reject_multi(self):
        ids = self._context.get('active_ids', False)
        records = self.env[self.model_name].browse(ids)
        records.write({'state': 'rejected', 'reject_reason': self.reject_reason})
        for rec in records:
            rec.sudo()._send_reject_email()
        return True

    def action_conditional_reject(self):
        record = self.env[self.model_name].browse(self.res_id)
        record.write({'state': 'rejected', 'reject_reason': self.reject_reason})
        record.sudo()._send_reject_email()
        return True

    def action_documentary_reject(self):
        if self.res_id:
            records = self.env[self.model_name].browse(self.res_id)
        elif self._context.get('active_ids'):
            records = self.env[self.model_name].browse(self._context.get('active_ids'))
        records.documentary_reject(self.reject_reason)
        return True
