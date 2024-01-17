# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDesempenoSettings(models.Model):
    _name = "hr.employee"
    _inherit = ['onsc.legajo']

    score_ids = fields.One2many('onsc.desempeno.score',string="Puntaje",compute="_compute_onsc_desempeno_score")

    def _compute_onsc_desempeno_score(self):
        Score = self.env['onsc.desempeno.score'].suspend_security()
        for record in self:
            record.score_ids = record.cv_digital_id.advanced_formation_ids.filtered(
                lambda x: x.documentary_validation_state == 'validated')
