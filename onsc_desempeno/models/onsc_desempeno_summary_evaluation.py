# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api
from odoo.osv import expression

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_definition', 'Definición de entorno'),
    ('gap_deal', 'Acuerdo de Brecha'),
    ('development_plan', 'Plan de desarrollo'),
    ('tracing_plan', 'Seguimiento del Plan de desarrollo'),

]

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

GAP_DEAL_STATES = [
    ('no_deal', 'Pendiente'),
    ('agree_leader', 'Acordado Líder'),
    ('agree_evaluated', 'Acordado Evaluado'),
    ('agree', 'Acordado'),
]


class ONSCLegajoSummaryEvaluation(models.Model):
    _name = "onsc.desempeno.summary.evaluation"
    _description = "Resumen de evaluaciones"
    _auto = False
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoSummaryEvaluation, self).fields_get(allfields, attributes)
        hide = ['type', 'order_type', 'order_state']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

        result = super(ONSCLegajoSummaryEvaluation, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count
        )
        if not result and not self._context.get('avoid_recursion', False):
            result = super(ONSCLegajoSummaryEvaluation, self).search([('show_evaluation_finished', '=', True)])
        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)

        return super(ONSCLegajoSummaryEvaluation, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count,
            access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        result = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if len(result) == 0:
            jokey_domain = [('show_evaluation_finished', '=', True)]
            result = super().read_group(jokey_domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                        lazy=lazy)
        return result

    def _get_domain(self, args):

        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        evaluations = [x for x in args if x[0] == 'evaluations']
        if evaluations:
            args_extended = [('state_summary', 'in', ['draft', 'in_process']),
                             ('evaluation_type', 'in',
                              ['self_evaluation', 'leader_evaluation', 'environment_evaluation', 'collaborator',
                               'tracing_plan']), ('inciso_id', '=', inciso_id),
                             ('operating_unit_id', '=', operating_unit_id),
                             ('evaluator_id', '=', self.env.user.employee_id.id), ]

            args_extended = expression.OR(
                [[('state_summary', 'in', ['draft', 'in_process']), ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluation_type', '=', 'environment_definition'),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)], args_extended])

            args_extended = expression.OR(
                [[('state_summary', 'in', ['draft', 'in_process']),
                  ('evaluation_type', 'in', ['gap_deal', 'development_plan']),
                  ('gap_deal_state', '=', 'no_deal'), '|', ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluator_id', '=', self.env.user.employee_id.id),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)], args_extended])
            args_extended = expression.OR(
                [[('state_summary', '=', 'in_process'), ('evaluation_type', 'in', ['gap_deal', 'development_plan']),
                  ('gap_deal_state', '=', 'agree_leader'), ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)],
                 args_extended])
            args_extended = expression.OR(
                [[('state_summary', '=', 'in_process'), ('evaluation_type', 'in', ['gap_deal', 'development_plan']),
                  ('gap_deal_state', '=', 'agree_evaluated'), ('evaluator_id', '=', self.env.user.employee_id.id),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)],
                 args_extended])
        else:
            args_extended = [
                ('evaluation_type', 'in',
                 ['self_evaluation', 'leader_evaluation', 'environment_evaluation', 'collaborator',
                  'tracing_plan']), ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id),
                ('evaluator_id', '=', self.env.user.employee_id.id), ]

            args_extended = expression.OR(
                [[('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluation_type', '=', 'environment_definition'),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)], args_extended])

            args_extended = expression.OR(
                [[('evaluation_type', 'in', ['gap_deal', 'development_plan']),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id),
                  '|', ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluator_id', '=', self.env.user.employee_id.id)], args_extended])

        return expression.AND([args_extended, args])

    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', required=True, readonly=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', readonly=True)
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador', readonly=True)
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado', readonly=True)
    evaluation_start_date = fields.Date(string='Fecha inicio ciclo evaluación')
    evaluation_end_date = fields.Date(string='Fecha fin ciclo evaluación')
    state_summary = fields.Selection(STATE, string='Estado', readonly=True)
    order_type = fields.Integer(string='Orden del tipo')
    evaluations = fields.Boolean(string="Mis evaluaciones pendientes")
    order_state = fields.Integer(string='Orden del tipo')
    gap_deal_state = fields.Selection(
        selection=GAP_DEAL_STATES,
        string="Subestado",
    )
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='UE', readonly=True)
    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación')

    type = fields.Selection(
        string='Tipo',
        selection=[('system', 'Sistema'),
                   ('joker', 'Comodity')],
        required=False)

    show_evaluation_finished = fields.Boolean(string='¿Ultimas evaluaciones finalizadas?',
                                              compute='_compute_show_evaluation_finished',
                                              search='_search_show_evaluation_finished')
    write_date = fields.Datetime('Fecha de última modificación', index=True, readonly=True)

    def button_open_evaluation(self):
        ctx = self.env.context.copy()
        if self.evaluation_type == 'gap_deal':
            ctx.update({'gap_deal': True})
        else:
            ctx.update({'gap_deal': False})

        if self.evaluation_type == 'development_plan':
            ctx.update({'develop_plan': True})
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_devlop_action').read()[0]
        elif self.evaluation_type == 'tracing_plan':
            ctx.update({'tracing_plan': True})
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_devlop_action').read()[0]
        else:
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_readonly_action').read()[0]
        action.update({'res_id': self.evaluation_id.id, 'context': ctx, })
        return action

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'onsc_desempeno_summary_evaluation')
        self.env.cr.execute('''CREATE OR REPLACE VIEW onsc_desempeno_summary_evaluation AS ( SELECT
            row_number() OVER(ORDER BY order_type,order_state) AS id, *
        FROM(
        SELECT evaluation_type,
                general_cycle_id,
                evaluator_id,
                evaluated_id,
                evaluation_start_date,
                evaluation_end_date,
                CASE
                    WHEN evaluation_type = 'gap_deal' THEN state_gap_deal
                    WHEN  evaluation_type = 'development_plan' THEN state_gap_deal
                    ELSE state
               END AS state_summary,
               CASE
                    WHEN evaluation_type = 'self_evaluation' THEN 1  -- Asigna un valor según el tipo de evaluación
                    WHEN evaluation_type = 'leader_evaluation' THEN 2
                    WHEN evaluation_type = 'environment_definition' THEN 3
                    WHEN evaluation_type = 'environment_evaluation' THEN 4
                    WHEN evaluation_type = 'collaborator' THEN 5
                    WHEN evaluation_type = 'gap_deal' THEN 6
                    WHEN evaluation_type = 'development_plan' THEN 7
                    WHEN evaluation_type = 'tracing_plan' THEN 8
               END AS order_type,
               False as evaluations,
               CASE WHEN state = 'draft' THEN 1
                    WHEN  state = 'in_process' THEN 2
                    ELSE 3
                END AS order_state,
               gap_deal_state,
               operating_unit_id,
               inciso_id,
               id as evaluation_id,
               'system' AS type,
               write_date
        FROM onsc_desempeno_evaluation
        WHERE year IN (EXTRACT(YEAR FROM CURRENT_DATE), EXTRACT(YEAR FROM CURRENT_DATE) - 1) and state != 'finished' and
        evaluation_type not in ('gap_deal','development_plan')
        UNION ALL
         SELECT evaluation_type,
                general_cycle_id,
                evaluator_id,
                evaluated_id,
                evaluation_start_date,
                evaluation_end_date,
                CASE
                    WHEN evaluation_type = 'gap_deal' THEN state_gap_deal
                    WHEN  evaluation_type = 'development_plan' THEN state_gap_deal
                    ELSE state
               END AS state_summary,
               CASE
                    WHEN evaluation_type = 'self_evaluation' THEN 1  -- Asigna un valor según el tipo de evaluación
                    WHEN evaluation_type = 'leader_evaluation' THEN 2
                    WHEN evaluation_type = 'environment_definition' THEN 3
                    WHEN evaluation_type = 'environment_evaluation' THEN 4
                    WHEN evaluation_type = 'collaborator' THEN 5
                    WHEN evaluation_type = 'gap_deal' THEN 6
                    WHEN evaluation_type = 'development_plan' THEN 7
                    WHEN evaluation_type = 'tracing_plan' THEN 8
               END AS order_type,
               False as evaluations,
               CASE WHEN state = 'draft' THEN 1
                    WHEN  state = 'in_process' THEN 2
                    ELSE 3
                END AS order_state,
               gap_deal_state,
               operating_unit_id,
               inciso_id,
               id as evaluation_id,
               'system' AS type,
               write_date
        FROM onsc_desempeno_evaluation
        WHERE year IN (EXTRACT(YEAR FROM CURRENT_DATE), EXTRACT(YEAR FROM CURRENT_DATE) - 1) and
         state_gap_deal != 'finished' and evaluation_type in ('gap_deal','development_plan')
        UNION ALL
        SELECT evaluation_type,
                general_cycle_id,
                evaluator_id,
                evaluated_id,
                evaluation_start_date,
                evaluation_end_date,
                CASE
                    WHEN evaluation_type = 'gap_deal' THEN state_gap_deal
                    WHEN  evaluation_type = 'development_plan' THEN state_gap_deal
                    ELSE state
               END AS state_summary,
               CASE
                    WHEN evaluation_type = 'self_evaluation' THEN 1  -- Asigna un valor según el tipo de evaluación
                    WHEN evaluation_type = 'leader_evaluation' THEN 2
                    WHEN evaluation_type = 'environment_definition' THEN 3
                    WHEN evaluation_type = 'environment_evaluation' THEN 4
                    WHEN evaluation_type = 'collaborator' THEN 5
                    WHEN evaluation_type = 'gap_deal' THEN 6
                    WHEN evaluation_type = 'development_plan' THEN 7
                    WHEN evaluation_type = 'tracing_plan' THEN 8
               END AS order_type,
               False as evaluations,
               CASE WHEN state = 'draft' THEN 1
                    WHEN  state = 'in_process' THEN 2
                    ELSE 3
                END AS order_state,
               gap_deal_state,
               operating_unit_id,
               inciso_id,
               id as evaluation_id,
               'joker' AS type,
               write_date
        FROM onsc_desempeno_evaluation
        WHERE year IN (EXTRACT(YEAR FROM CURRENT_DATE), EXTRACT(YEAR FROM CURRENT_DATE) - 1) and
        state_gap_deal = 'finished' and evaluation_type in ('gap_deal','development_plan')
        UNION ALL
        SELECT evaluation_type,
                general_cycle_id,
                evaluator_id,
                evaluated_id,
                evaluation_start_date,
                evaluation_end_date,
                CASE
                    WHEN evaluation_type = 'gap_deal' THEN state_gap_deal
                    WHEN  evaluation_type = 'development_plan' THEN state_gap_deal
                    ELSE state
               END AS state_summary,
               CASE
                    WHEN evaluation_type = 'self_evaluation' THEN 1  -- Asigna un valor según el tipo de evaluación
                    WHEN evaluation_type = 'leader_evaluation' THEN 2
                    WHEN evaluation_type = 'environment_definition' THEN 3
                    WHEN evaluation_type = 'environment_evaluation' THEN 4
                    WHEN evaluation_type = 'collaborator' THEN 5
                    WHEN evaluation_type = 'gap_deal' THEN 6
                    WHEN evaluation_type = 'development_plan' THEN 7
                    WHEN evaluation_type = 'tracing_plan' THEN 8
               END AS order_type,
               False as evaluations,
               CASE WHEN state = 'draft' THEN 1
                    WHEN  state = 'in_process' THEN 2
                    ELSE 3
                END AS order_state,
               gap_deal_state,
               operating_unit_id,
               inciso_id,
               id as evaluation_id,
               'joker' AS type,
               write_date
        FROM onsc_desempeno_evaluation
        WHERE year IN (EXTRACT(YEAR FROM CURRENT_DATE), EXTRACT(YEAR FROM CURRENT_DATE) - 1) and state = 'finished' and
        evaluation_type not in ('gap_deal','development_plan')) as main_query)''')

    def _search_show_evaluation_finished(self, operator, value):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        result = self.browse()
        args_extended = [('type', '=', 'joker'),
                         ('evaluation_type', 'in',
                          ['self_evaluation', 'leader_evaluation', 'environment_evaluation', 'collaborator',
                           'tracing_plan', 'gap_deal', 'development_plan']), ('inciso_id', '=', inciso_id),
                         ('operating_unit_id', '=', operating_unit_id),
                         ('evaluator_id', '=', self.env.user.employee_id.id), ]

        joker_records = self.with_context(avoid_recursion=True).search(args_extended,
                                                                       order='evaluation_type, evaluator_id, write_date DESC', )
        seen_combinations = set()
        for record in joker_records:
            combination = (record.evaluation_type, record.evaluator_id.id)
            if combination not in seen_combinations:
                result += record
                seen_combinations.add(combination)

        args_extended = [('type', '=', 'joker'), ('evaluated_id', '=', self.env.user.employee_id.id),
                         ('evaluation_type', 'in', ['gap_deal', 'development_plan', 'environment_definition']),
                         ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)]
        joker_records = self.with_context(avoid_recursion=True).search(args_extended,
                                                                       order='evaluation_type, evaluated_id, write_date DESC')

        seen_combinations = set()
        for record in joker_records:
            combination = (record.evaluation_type, record.evaluated_id.id)
            if combination not in seen_combinations:
                result += record
                seen_combinations.add(combination)

        if operator == '=' and value is False:
            _operator = 'not in'
        else:
            _operator = 'in'
        return [('id', _operator, result.ids)]

    def _compute_show_evaluation_finished(self):
        for record in self:
            record.show_evaluation_finished = True
