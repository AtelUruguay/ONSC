# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api


class ONSCDesempenoEvalaluatiorChangeWizard(models.TransientModel):
    _name = 'onsc.desempeno.evaluation.change.wizard'
    _description = 'Cambio de evaluador'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación', required=True)
    reasign_tome = fields.Boolean(
        string='Reasignarme evaluación')
    job_id = fields.Many2one('hr.job', string='Nuevo evaluador', required=False)
    reason_id = fields.Many2one('onsc.desempeno.reason.change.evaluator', string='Motivo de cambio', required=False)

    is_reasign_tome_available = fields.Boolean(
        string=u'¿Puedo reasignarme evaluación?',
        compute='_compute_is_reasign_tome_available'
    )

    is_reason_id_available = fields.Boolean(
        string=u'¿Puedo asignar Motivo de cambio?',
        compute='_compute_is_reason_id_available'
    )

    job_id_domain = fields.Char(compute='_compute_evaluator_id_domain')

    @api.onchange('reasign_tome')
    def _onchange_reasign_tome(self):
        self.job_id = False

    @api.depends('evaluation_id')
    def _compute_is_reasign_tome_available(self):
        for rec in self:
            is_iam_original_eval = rec.evaluation_id.original_evaluator_id.id == self.env.user.employee_id.id
            is_iam_current_eval = rec.evaluation_id.evaluator_id.id == self.env.user.employee_id.id
            rec.is_reasign_tome_available = is_iam_original_eval and not is_iam_current_eval

    @api.depends('evaluation_id', 'job_id')
    def _compute_is_reason_id_available(self):
        is_gh_responsable = self.evaluation_id._is_group_responsable_uo()
        is_usuario_gh = self.user_has_groups(
            'onsc_desempeno.group_desempeno_usuario_gh_ue,onsc_desempeno.group_desempeno_usuario_gh_inciso')
        user_job = self.env.user.employee_id.job_id

        if self.evaluation_id.evaluation_type == 'leader_evaluation':
            self.is_reason_id_available = True
        elif is_usuario_gh and self.job_id.id != user_job.id:
            self.is_reason_id_available = True
        elif is_gh_responsable:
            Department = self.env['hr.department'].sudo()
            employee = self.env.user.employee_id
            hierarchy_deparments = Department.search([('id', 'child_of', employee.job_id.department_id.id)])
            hierarchy_deparments |= employee.job_id.department_id
            is_responsable = is_gh_responsable and self.evaluation_id.uo_id.id in hierarchy_deparments.ids
            self.is_reason_id_available = is_responsable
        else:
            self.is_reason_id_available = False

    @api.depends('evaluation_id')
    def _compute_evaluator_id_domain(self):
        Job = self.env['hr.job'].sudo()
        is_usuario_gh = self.user_has_groups(
            'onsc_desempeno.group_desempeno_usuario_gh_ue,onsc_desempeno.group_desempeno_usuario_gh_inciso')
        user_job = self.env.user.employee_id.job_id
        for rec in self:
            is_leader_eval = self.evaluation_id.evaluation_type == 'leader_evaluation'
            # SI SOY RESPONSABLE EN LA LINEA JERARQUICA DE LA UO ORIGINAL DE LA EVALUACIÓN ME PUEDO ASIGNAR A MI MISMO
            uo = self.evaluation_id.original_evaluator_uo_id or self.evaluation_id.evaluator_uo_id
            managers_in_department_tree = uo.get_all_managers_in_department_tree()
            if self.env.user.employee_id.id in managers_in_department_tree or is_usuario_gh and not is_leader_eval:
                jobs = user_job
            else:
                jobs = self.env['hr.job']

            is_order_1 = self.evaluation_id.sudo().evaluator_uo_id.hierarchical_level_id.order == 1
            if is_usuario_gh and is_leader_eval:
                jobs |= Job.search([
                    ('department_id.parent_id', '=', self.evaluation_id.evaluator_uo_id.id),
                    ('department_id.function_nature', '=', 'adviser'),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])
                jobs |= Job.search([
                    ('department_id', '=', self.evaluation_id.evaluator_uo_id.id),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])
            elif is_usuario_gh and not is_leader_eval and is_order_1:
                jobs |= Job.search([
                    ('department_id.parent_id', '=', self.evaluation_id.evaluator_uo_id.id),
                    ('department_id.function_nature', '=', 'adviser'),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])
                jobs |= Job.search([
                    ('department_id', '=', self.evaluation_id.evaluator_uo_id.id),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())])
            rec.job_id_domain = json.dumps([
                ('id', 'in', jobs.ids),
                ('employee_id', 'not in', [self.evaluation_id.evaluated_id.id, self.evaluation_id.evaluator_id.id]),
            ])

    def action_confirm(self):
        if self.reason_id:
            reason_id = self.reason_id.id
        else:
            reason_id = self.env['onsc.desempeno.reason.change.evaluator'].search([('agree', '=', True)], limit=1).id
        if self.reasign_tome:
            vals = {
                'reason_change_id': reason_id,
                'evaluator_id': self.evaluation_id.original_evaluator_id.id,
                'evaluator_current_job_id': self.env.user.employee_id.job_id,
                'evaluator_uo_id': self.evaluation_id.original_evaluator_uo_id.id
            }
        else:
            vals = {
                'reason_change_id': reason_id,
                'evaluator_id': self.job_id.employee_id.id,
                'evaluator_current_job_id': self.job_id.id,
                'evaluator_uo_id': self.job_id.department_id.id
            }
        if not self.evaluation_id.original_evaluator_id:
            vals['original_evaluator_id'] = self.evaluation_id.evaluator_id.id
            vals['original_evaluator_uo_id'] = self.evaluation_id.evaluator_uo_id.id
        if not self.reason_id:
            vals['use_original_evaluator'] = True
        self.evaluation_id.suspend_security().write(vals)
