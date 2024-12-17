# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.desempeno.stage.extend.deadline.wizard'
    _description = 'Extender plazo'

    stage_id = fields.Many2one('onsc.desempeno.evaluation.stage', string='Evaluación', required=True)
    end_date = fields.Date(string=u'Fecha fin', required=True, tracking=True)

    @api.constrains('end_date', 'stage_id')
    def _check_end_date(self):
        for record in self:
            if record.end_date < fields.Date.today():
                raise ValidationError(_("La fecha fin debe ser mayor o igual a la fecha actual"))
            rule1 = record.end_date and record.stage_id.general_cycle_id.date_limit_toextend_360
            if rule1 and record.end_date > record.stage_id.general_cycle_id.date_limit_toextend_360:
                raise ValidationError(_("La fecha fin debe ser menor o igual a la "
                                        "Fecha límite para la extensión de Etapa 360°"))

    def action_confirm(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Evaluation.search(
            [('evaluation_stage_id', '=', self.stage_id.id), ('state', '!=', 'canceled'),
             ('evaluation_type', 'in', ['environment_evaluation', 'collaborator'])]).write(
            {'locked': False})
        self.stage_id.suspend_security().write({'end_date': self.end_date})
