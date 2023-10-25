# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.desempeno.evaluation.change.wizard'
    _description = 'Cambio de evaluador'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación', required=True)
    job_id = fields.Many2one('hr.job', string='Nuevo evaluador', required=True)
    reason_id = fields.Many2one('onsc.desempeno.reason.change.evaluator', string='Motivo de cambio', required=True)

    job_id_domain = fields.Char(compute='_compute_evaluator_id_domain')

    @api.depends('evaluation_id')
    def _compute_evaluator_id_domain(self):
        Job = self.env['hr.job'].sudo()
        is_usuario_gh = self.user_has_groups(
            'onsc_desempeno.group_desempeno_usuario_gh_ue,onsc_desempeno.group_desempeno_usuario_gh_inciso')
        for rec in self:
            # SI SOY RESPONSABLE EN LA LINEA JERARQUICA DE LA UO DE LA EVALUACIÓN ME PUEDO ASIGNAR A MI MISMO
            managers_in_department_tree = self.evaluation_id.evaluator_uo_id.get_all_managers_in_department_tree()
            if self.env.user.employee_id.id in managers_in_department_tree:
                jobs = self.env.user.employee_id.job_id
            else:
                jobs = self.env['hr.job']
            if is_usuario_gh:
                jobs = Job.search([
                    ('department_id.parent_id', '=', self.evaluation_id.evaluator_uo_id.id),
                    ('department_id.function_nature', '=', 'adviser'),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])
                jobs |= Job.search([
                    ('department_id', '=', self.evaluation_id.evaluator_uo_id.id),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])


            rec.job_id_domain = json.dumps([
                ('id', 'in', jobs.ids),
                ('employee_id', '!=', self.evaluation_id.evaluated_id.id)])

    def action_confirm(self):
        vals = {
            'reason_change_id': self.reason_id.id,
            'evaluator_id': self.job_id.employee_id.id,
            'evaluator_uo_id': self.job_id.department_id.id
        }
        if not self.evaluation_id.original_evaluator_id:
            vals['original_evaluator_id'] = self.evaluation_id.evaluator_id.id
        self.evaluation_id.suspend_security().write(vals)
