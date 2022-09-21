# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVRejectWizard(models.TransientModel):
    _name = 'onsc.cv.reject.wizard'
    _description = 'Rechazo de validación'

    reject_reason = fields.Text(string=u'Motivo de rechazo', required=True)
    model_name = fields.Char(string='Modelo relacionado')
    res_id = fields.Integer("Id del registro relacionado")

    def action_reject(self):
        if self._context.get('is_documentary_reject'):
            return self.action_documentary_reject()
        else:
            return self.action_conditional_reject()

    def action_conditional_reject(self):
        record = self.env[self.model_name].browse(self.res_id)
        record.write({'state': 'rejected', 'reject_reason': self.reject_reason})
        record.sudo()._send_reject_email()
        return True

    def action_documentary_reject(self):
        record = self.env[self.model_name].browse(self.res_id)
        record.write({
            'documentary_validation_state': 'rejected',
            'documentary_reject_reason': self.reject_reason,
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        })
        return True
