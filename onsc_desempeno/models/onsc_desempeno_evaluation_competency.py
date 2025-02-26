# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Borrador'),
    ('in_process', 'En Proceso'),
    ('completed', 'Completado'),
    ('finished', 'Finalizado'),
    ('uncompleted', 'Sin Finalizar'),
    ('canceled', 'Cancelado'),
    ('deal_close', "Acuerdo cerrado")
]

HTML_HELP = """<a class="btn" style="padding-top:inherit!important;" target="_blank" title="%s"><i class="fa fa-question-circle-o" role="img" aria-label="Info"/></a>"""


class ONSCDesempenoEvaluationCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.competency'
    _description = u'Competencia'
    _order = "skill_id"

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True,
                                    ondelete='cascade')
    consolidate_id = fields.Many2one('onsc.desempeno.consolidated', string='Competencia', readonly=True,
                                     ondelete='set null')
    gap_deal_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True, ondelete='set null')
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    state_deal = fields.Selection(STATE, string='Estado', related='gap_deal_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    skill_line_ids = fields.Many2many(
        comodel_name="onsc.desempeno.skill.line",
        relation="competency_skill_line_rel",
        string="Lineas de competencia")
    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo',
                                required=False, ondelete='restrict')
    improvement_areas = fields.Text(string='Brecha/Fortalezas/Aspectos a mejorar', required=False)
    evaluation_form_edit = fields.Boolean('Puede editar el form?', related='evaluation_id.evaluation_form_edit', )
    order = fields.Integer('Orden')
    locked = fields.Boolean('Bloqueado', related='evaluation_id.locked')

    skill_tooltip = fields.Html(
        compute=lambda s: s._get_help('skill_tooltip'),
        default=lambda s: s._get_help('skill_tooltip', True))
    competency_form_edit = fields.Boolean('Puede editar el form?', compute='_compute_competency_form_edit')
    is_improvement_areas_help_form_active = fields.Boolean(
        compute=lambda s: s._get_value_config('is_improvement_areas_help_form_active'),
        default=lambda s: s._get_value_config('is_improvement_areas_help_form_active', True)
    )
    improvement_areas_help_text = fields.Text(
        compute=lambda s: s._get_value_config('improvement_areas_help_text'),
        default=lambda s: s._get_value_config('improvement_areas_help_text', True)
    )
    grade_suggested_id = fields.Many2one(
        'onsc.desempeno.grade.equivalence',
        string='Grado de necesidad de desarrollo sugerido',
        compute='_compute_grade_suggested',
        store=True
    )

    def _get_value_config(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    @api.depends('state', 'state_deal')
    def _compute_competency_form_edit(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            if self._context.get('readonly_evaluation'):
                condition = True
            elif record.gap_deal_id:
                _cond1 = record.gap_deal_id.state_gap_deal != 'in_process' or record.gap_deal_id.gap_deal_state != 'no_deal'
                _cond2 = record.gap_deal_id.evaluator_id.id != user_employee_id and record.gap_deal_id.evaluated_id.id != user_employee_id
                condition = _cond1 or _cond2
            else:
                _cond1 = record.evaluation_id.evaluator_id.id != user_employee_id or record.evaluation_id.locked
                condition = record.state not in ['in_process'] or _cond1
            record.competency_form_edit = condition

    @api.depends('skill_line_ids','skill_line_ids.frequency_id')
    def _compute_grade_suggested(self):
        EquivalenceGrade = self.env['onsc.desempeno.grade.equivalence']
        for record in self:
            frequency_float_list = []
            for skill_line_id in record.skill_line_ids:
                frequency_id = skill_line_id.frequency_id
                if frequency_id and frequency_id.value != float(0):
                    frequency_float_list.append(frequency_id.value)
            if frequency_float_list:
                average_frequency = sum(frequency_float_list) / len(frequency_float_list)
            else:
                average_frequency = float(0)
            record.grade_suggested_id = EquivalenceGrade.get_grade_equivalence(average_frequency)

    def _get_help(self, help_field='', is_default=False):
        _html2construct = HTML_HELP % ('Tooltip')
        if is_default:
            return eval("_html2construct")
        for rec in self:
            _html2construct = HTML_HELP % (rec.suspend_security().skill_id.definition or '')
            setattr(rec, help_field, _html2construct)

    def button_open_current_skill(self):
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_competency_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
