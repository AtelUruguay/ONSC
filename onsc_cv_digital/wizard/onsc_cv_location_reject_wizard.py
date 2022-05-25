# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVLocation(models.Model):
    _name = 'onsc.cv.location.reject.wizard'
    _description = 'Rechazo de Validación de Ciudad/Localidad'

    reject_reason = fields.Char(string=u'Motivo de rechazo', required=True)

    def action_reject(self):
        locations = self.env['onsc.cv.location'].browse(self.env.context.get('active_ids'))
        locations.write({'state': 'rejected', 'reject_reason': self.reject_reason})
