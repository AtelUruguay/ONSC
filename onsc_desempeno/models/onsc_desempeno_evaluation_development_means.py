# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api


_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Borrador'),
    ('in_process', 'En Proceso'),
    ('completed', 'Completado'),
    ('deal_close', "Acuerdo cerrado"),
    ('agreed_plan', "Plan Acordado"),
    ('uncompleted', 'Sin Finalizar'),
    ('finished', 'Finalizado'),
    ('canceled', 'Cancelado')
]

HTML_HELP = """<a class="btn" style="padding-top:inherit!important;" target="_blank" title="%s"><i class="fa fa-question-circle-o" role="img" aria-label="Info"/></a>"""


class ONSCDesempenoEvaluatioDevelopmentCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.development.competency'
    _description = u'Competencias'
    _rec_name = 'skill_id'
    _order = "skill_id"

    evaluation_id = fields.Many2one(
        'onsc.desempeno.evaluation',
        string='Evaluacion',
        readonly=True,
        ondelete='cascade')
    tracing_id = fields.Many2one(
        'onsc.desempeno.evaluation',
        string='Evaluacion',
        readonly=True,
        ondelete='cascade')
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    development_goal = fields.Text('Objetivo de desarrollo')
    development_means_ids = fields.One2many('onsc.desempeno.evaluation.development.means', 'competency_id',
                                            string='Medios de desarrollo')
    tracing_means_ids = fields.One2many('onsc.desempeno.evaluation.development.means', 'competency_id',
                                        string='Medios de desarrollo')
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    should_disable_form_edit = fields.Boolean('Puede editar el form?', compute='_compute_should_disable_form_edit')
    state_deal = fields.Selection(STATE, string='Estado', related='evaluation_id.state_gap_deal', readonly=True)
    is_tracing = fields.Boolean("Es seguimiento?", compute='_compute_is_tracing')
    is_required = fields.Boolean("Es requerido?", compute='_compute_is_required')

    @api.depends('state_deal', 'state')
    def _compute_should_disable_form_edit(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            if record.evaluation_id.evaluation_type == 'development_plan':
                _cond1 = record.evaluation_id.state_gap_deal != 'in_process' or record.evaluation_id.gap_deal_state != 'no_deal'
                _cond2 = record.evaluation_id.evaluator_id.id != user_employee_id and record.evaluation_id.evaluated_id.id != user_employee_id
            else:
                _cond1 = record.tracing_id.state != 'in_process'

                _cond2 = record.tracing_id.evaluator_id.id != user_employee_id
            condition = _cond1 or _cond2

            record.should_disable_form_edit = condition

    @api.depends('development_means_ids', 'tracing_means_ids')
    def _compute_is_required(self):
        for record in self:
            record.is_required = len(record.development_means_ids) > 0 or len(record.tracing_means_ids) > 0

    @api.depends('state_deal', 'state')
    def _compute_is_tracing(self):
        for record in self:
            record.is_tracing = record.evaluation_id.evaluation_type != 'development_plan'

    def button_open_current_competency(self):
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_develop_competency_action').read()[0]
        action.update({'res_id': self.id, 'target': 'current'})
        return action

    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def button_custom_navigation_back(self):

        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('onsc_desempeno.onsc_desempeno_develop_plan_form').id,
            'res_model': 'onsc.desempeno.evaluation',
            'target': 'main',
            'res_id': self.tracing_id.id or self.evaluation_id.id,
        }
        return action


class ONSCDesempenoEvaluatioDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.evaluation.development.means'
    _description = u'Evaluación: Medios de desarrollo'

    def _is_group_responsable_uo(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_responsable_uo')

    competency_id = fields.Many2one(
        'onsc.desempeno.evaluation.development.competency',
        string='Competencia',
        required=True,
        ondelete='cascade')

    skill_id = fields.Many2one(related='competency_id.skill_id', string='Competencia')
    agreed_activities = fields.Text('Actividades acordadas', required=True)
    comments = fields.Text('Comentarios')
    detail_activities = fields.Text('Detalle de actividades', required=True)
    means_id = fields.Many2one('onsc.desempeno.development.means', string='Medio de desarrollo',
                               required=True)
    tracing_plan_ids = fields.One2many(
        'onsc.desempeno.evaluation.tracing.plan',
        'develop_means_id',
        string='Seguimiento del plan de desarrollo',
        ondelete='cascade')
    means_form_edit = fields.Boolean('Puede editar el form?', compute='_compute_mean_form_edit')
    show_buttons = fields.Boolean(string="Boton seguimiento", compute='_compute_show_buttons')

    last_tracing_plan_id = fields.Many2one(
        'onsc.desempeno.evaluation.tracing.plan',
        string='Ultimo seguimiento',
        compute='_compute_last_tracing_plan_id',
        store=True
    )
    is_canceled = fields.Boolean(
        string='¿Está cancelada?',
        compute='_compute_last_tracing_plan_id',
        store=True
    )

    means_tooltip = fields.Html(compute='_get_help')

    @api.depends('means_id')
    def _get_help(self):
        for rec in self:
            _html2construct = HTML_HELP % (rec.suspend_security().means_id.description or '')
            rec.means_tooltip = _html2construct

    @api.depends('competency_id')
    def _compute_mean_form_edit(self):
        employee_id = self.env.user.employee_id
        for record in self:
            record.means_form_edit = record.competency_id.tracing_id.state != 'in_process' or record.competency_id.tracing_id.evaluator_id.id != employee_id.id

    @api.depends('competency_id')
    def _compute_show_buttons(self):
        for record in self:
            record.show_buttons = record.competency_id.tracing_id.evaluation_type == 'tracing_plan'

    @api.depends('tracing_plan_ids')
    def _compute_last_tracing_plan_id(self):
        for record in self:
            if len(record.tracing_plan_ids):
                last_tracing_plan_id = record.tracing_plan_ids[-1]
                record.last_tracing_plan_id = last_tracing_plan_id.id
                record.is_canceled = last_tracing_plan_id.degree_progress_id.is_cancel_flow
            else:
                record.last_tracing_plan_id = False
                record.is_canceled = False

    def button_open_tracing(self):
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evalution_development_means_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


class ONSCDesempenoEvaluatioTracingPlan(models.Model):
    _name = 'onsc.desempeno.evaluation.tracing.plan'
    _description = u'Seguimiento del plan de desarrollo'

    develop_means_id = fields.Many2one('onsc.desempeno.evaluation.development.means', string='Medio de desarrollo')
    tracing_plan_date = fields.Date('Fecha de seguimiento de la actividad', default=fields.Date.context_today,
                                    readonly=True)
    comments = fields.Text('Observaciones')
    degree_progress_id = fields.Many2one('onsc.desempeno.degree.progress', string='Grado de avance', required=True)
    created = fields.Boolean("Creado", default=False)

    @api.model
    def create(self, values):
        values['created'] = True
        res = super(ONSCDesempenoEvaluatioTracingPlan, self).create(values)
        return res
