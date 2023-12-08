# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluatioDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.evaluation.development.means'
    _description = u'Medios de desarrollo'

    def _is_group_responsable_uo(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_responsable_uo')

    competency_id = fields.Many2one(
        'onsc.desempeno.evaluation.development.competency',
        string='Competencia',
        required=True,
        ondelete='cascade')
    skill_id = fields.Many2one(related='competency_id.skill_id', string='Competencia')
    agreed_activities = fields.Text('Actividades acordadas', required=True)
    comments = fields.Text('Comentarios', required=True)
    detail_activities = fields.Text('Detalle de actividades', required=True)
    means_id = fields.Many2one('onsc.desempeno.development.means', string='Medio de desarrollo',
                               required=True)
    tracing_plan_ids = fields.One2many(
        'onsc.desempeno.evaluation.tracing.plan',
        'develop_means_id',
        string='Seguimiento del plan de desarrollo',
        ondelete='cascade')
    means_form_edit = fields.Boolean('Puede editar el form?', compute='_compute_mean_form_edit')

    @api.depends('competency_id')
    def _compute_mean_form_edit(self):
        employee_id = self.env.user.employee_id
        Department = self.env['hr.department'].sudo()
        for record in self:
            _cond1 = record.competency_id.evaluation_id.state_gap_deal != 'in_process' or record.competency_id.evaluation_id.evaluator_id.id != employee_id.id
            hierarchy_deparments = Department.search([('id', 'child_of', employee_id.job_id.department_id.id)])
            hierarchy_deparments |= employee_id.job_id.department_id
            _cond2 = self._is_group_responsable_uo() and record.competency_id.evaluation_id.uo_id.id in hierarchy_deparments.ids
            record.means_form_edit = _cond1 or not _cond2

    def button_open_tracing(self):
        return {
            'view_mode': 'form',
            'res_model': 'onsc.desempeno.evaluation.development.means',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            'views': [[self.env.ref('onsc_desempeno.onsc_desempeno_tracing_development_means_form').id, 'form'],
                      [False, 'list']],
        }

    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


class ONSCDesempenoEvaluatioDevelopmentCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.development.competency'
    _description = u'Competencias'
    _order = "skill_id"

    evaluation_id = fields.Many2one(
        'onsc.desempeno.evaluation',
        string='Evaluacion',
        readonly=True,
        ondelete='cascade')
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    development_goal = fields.Text('Objetivo de desarrollo')
    development_means_ids = fields.One2many('onsc.desempeno.evaluation.development.means', 'competency_id',
                                            string='Medios de desarrollo')


class ONSCDesempenoEvaluatioTracingPlan(models.Model):
    _name = 'onsc.desempeno.evaluation.tracing.plan'
    _description = u'Seguimiento del plan de desarrollo'

    develop_means_id = fields.Many2one('onsc.desempeno.evaluation.development.means', string='Medio de desarrollo')
    tracing_plan_date = fields.Date('Fecha de seguimiento de la actividad', default=fields.Date.context_today,
                                    readonly=True)
    comments = fields.Text('Observaciones')
    degree_progress_id = fields.Many2one('onsc.desempeno.degree.progress', string='Grado de avance', required=True)
