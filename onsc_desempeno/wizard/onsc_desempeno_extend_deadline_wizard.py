# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.desempeno.stage.extend.deadline.wizard'
    _description = 'Extender plazo'

    stage_id = fields.Many2one('onsc.desempeno.evaluation.stage', string='Evaluación', required=True)
    end_date = fields.Date(string=u'Fecha fin', required=True, tracking=True)

    @api.constrains('end_date')
    def _check_end_date(self):
        for record in self:
            if record.end_date < fields.Date.today():
                raise ValidationError(_("La fecha fin debe ser mayor o igual a la fecha actual"))

    def action_confirm(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Evaluation.search(
            [('evaluation_stage_id', '=', self.stage_id.id), ('state', '!=', 'canceled'),
             ('evaluation_type', 'in', ['environment_evaluation', 'collaborator'])]).write(
            {'locked': False})
        self.stage_id.suspend_security().write({'end_date': self.end_date})
