# -*- coding: utf-8 -*-
import ast
import logging

from odoo import fields, models, api
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ONSCDesempenoScore(models.Model):
    _name = 'onsc.desempeno.score'
    _description = u'Desempeño - Puntajes'

    def _get_domain(self, args):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id

        if self.user_has_groups('onsc_desempeno.group_desempeno_administrador'):
            args_extended = [(1, '=', 1)]
        elif self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso'):
            args_extended = [('inciso_id', '=', inciso_id)]
        elif self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue'):
            args_extended = [('operating_unit_id', '=', operating_unit_id)]
        else:
            args_extended = []
        return expression.AND([args_extended, args])

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
            args = self._get_domain(args)
        return super(ONSCDesempenoScore, self)._search(args, offset=offset, limit=limit, order=order,
                                                       count=count,
                                                       access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    year = fields.Integer(u'Año', index=True, group_operator=False)
    # year_char = fields.Char(u'Año (mostrar en la vista lista)', index=True, compute='_compute_year')
    evaluation_stage_id = fields.Many2one(
        'onsc.desempeno.evaluation.stage',
        string='Evaluación 360')
    evaluation_list_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list',
        string='Lista de participantes')
    inciso_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso',
        index=True)
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora",
        index=True)
    department_id = fields.Many2one(
        "hr.department",
        string="Unidad organizativa",
        required=True,
        index=True)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Evaluador",
        store=True,
        index=True)

    evaluations_360_total_qty = fields.Integer('Evaluaciones 360')
    evaluations_360_finished_qty = fields.Integer('Evaluaciones 360 finalizadas')

    evaluations_360_score = fields.Float('Puntaje 360 base')
    evaluations_360_finished_score = fields.Float('Puntaje 360')

    evaluations_gap_deal_finished_score = fields.Float('Puntaje Acuerdo de brecha')
    evaluations_develop_plan_finished_score = fields.Float('Puntaje Plan de desarrollo')
    evaluations_tracing_plan_finished_score = fields.Float('Puntaje Seguimiento del Plan de desarrollo')
    evaluations_tracing_plan_activity_score = fields.Float('Puntaje de Actividad de Seguimiento del Plan de desarrollo')
    score = fields.Float('Puntaje final')
    is_employee_notified = fields.Boolean(string='¿Fue notificado?')
    is_pilot = fields.Boolean(string="¿Es piloto?")
    whitout_impact = fields.Boolean(string="Sin impacto en legajo")

    def button_open_gap_deal(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        ids = Evaluation.search([('evaluation_type', '=', 'gap_deal'),
                                 ('evaluated_id', '=', self.employee_id.id),
                                 ('inciso_id', '=', self.inciso_id.id),
                                 ('operating_unit_id', '=', self.operating_unit_id.id),
                                 ('evaluation_stage_id', '=', self.evaluation_stage_id.id)]).ids
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_gap_deal_evaluation_action').read()[0]
        _context = ast.literal_eval(action.get('context', {}))
        _context['ignore_security_rules'] = True
        _context['ignore_base_restrict'] = True
        action.update({'domain': [('id', 'in', ids)], 'target': 'current', 'context': _context})
        return action

    def button_open_development_plan(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        ids = Evaluation.search([('evaluation_type', '=', 'development_plan'),
                                 ('evaluated_id', '=', self.employee_id.id),
                                 ('inciso_id', '=', self.inciso_id.id),
                                 ('operating_unit_id', '=', self.operating_unit_id.id),
                                 ('evaluation_stage_id', '=', self.evaluation_stage_id.id)]).ids
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_develop_plan_action').read()[0]
        _context = ast.literal_eval(action.get('context', {}))
        _context['ignore_security_rules'] = True
        _context['ignore_base_restrict'] = True
        action.update({'domain': [('id', 'in', ids)], 'target': 'current', 'context': _context})
        return action

    def button_open_tracing_plan(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        ids = Evaluation.search([('evaluation_type', '=', 'tracing_plan'),
                                 ('evaluated_id', '=', self.employee_id.id),
                                 ('inciso_id', '=', self.inciso_id.id),
                                 ('operating_unit_id', '=', self.operating_unit_id.id),
                                 ('evaluation_stage_id', '=', self.evaluation_stage_id.id)]).ids
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_tracing_plan_action').read()[0]
        _context = ast.literal_eval(action.get('context', {}))
        _context['ignore_security_rules'] = True
        _context['ignore_base_restrict'] = True
        action.update({'domain': [('id', 'in', ids)], 'target': 'current', 'context': _context})
        return action
