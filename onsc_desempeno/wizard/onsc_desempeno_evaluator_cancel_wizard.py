# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.desempeno.evaluation.cancel.wizard'
    _description = 'Cancelar evaluación'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación', required=True)
    reason_id = fields.Many2one('onsc.desempeno.reason.cancellation', string='Motivo de cancelación', required=True)

    def action_confirm(self):

        if self.evaluation_id.evaluation_type in ('gap_deal', 'development_plan'):
            vals = {
                'reason_cancel_id': self.reason_id.id,
                'state_before_cancel': self.evaluation_id.state_gap_deal,
                'state_gap_deal': 'canceled',
            }

        else:
            vals = {
                'reason_cancel_id':  self.reason_id.id,
                'state_before_cancel': self.evaluation_id.state,
                'state': 'canceled',
            }

        self.evaluation_id.suspend_security().write(vals)
