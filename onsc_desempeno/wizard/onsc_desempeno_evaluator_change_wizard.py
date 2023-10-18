# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.desempeno.evaluation.change.wizard'
    _description = 'Cambio de evaluador'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación', required=True)
    evaluator_id = fields.Many2one('hr.employee', string='Nuevo evaluador', required=True)
    reason_id = fields.Many2one('onsc.desempeno.reason.change.evaluator', string='Motivo de cambio', required=True)

    evaluator_id_domain = fields.Char(compute='_compute_evaluator_id_domain')

    @api.depends('evaluation_id')
    def _compute_evaluator_id_domain(self):
        Job = self.env['hr.job'].sudo()
        is_usuario_gh = self.user_has_groups(
            'onsc_desempeno.group_desempeno_usuario_gh_ue,onsc_desempeno.group_desempeno_usuario_gh_inciso')
        is_responsable_uo = self.user_has_groups('onsc_desempeno.group_desempeno_responsable_uo')

        for rec in self:
            employees = self.env.user.employee_id
            if is_usuario_gh and not is_responsable_uo:
                employees |= Job.search([
                    ('department_id.parent_id', '=', self.evaluation_id.uo_id.id),
                    ('department_id.function_nature', '=', 'adviser'),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())]).mapped('emplyoee_id')
            rec.evaluator_id_domain = json.dumps([('id', 'in', employees.ids)])

    def action_confirm(self):
        vals = {
            'evaluator_id': self.evaluator_id
        }
        if not self.evaluation_id.original_evaluator_id:
            vals['original_evaluator_id'] = self.evaluation_id.evaluator_id.id
        self.evaluation_id.suspend_security().write(vals)
