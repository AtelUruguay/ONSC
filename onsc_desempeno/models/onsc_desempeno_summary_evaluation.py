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
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)

        return super(ONSCLegajoSummaryEvaluation, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count,
                                                                access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def _get_domain(self, args):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        evaluations = [x for x in args if x[0] == 'evaluations']
        if evaluations:
            args_extended = [('state', 'in', ['draft', 'in_process']),
                             ('evaluation_type', 'in',
                              ['self_evaluation', 'leader_evaluation', 'environment_evaluation', 'collaborator',
                               'tracing_plan']), ('inciso_id', '=', inciso_id),
                             ('operating_unit_id', '=', operating_unit_id),
                             ('evaluator_id', '=', self.env.user.employee_id.id), ]

            args_extended = expression.OR(
                [[('state', 'in', ['draft', 'in_process']), ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluation_type', '=', 'environment_definition'),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)], args_extended])

            args_extended = expression.OR(
                [[('state', 'in', ['draft', 'in_process']), ('evaluation_type', 'in', ['gap_deal', 'development_plan']),
                  ('gap_deal_state', '=', 'no_deal'), '|', ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluator_id', '=', self.env.user.employee_id.id),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)], args_extended])
            args_extended = expression.OR(
                [[('state', '=', 'in_process'), ('evaluation_type', 'in', ['gap_deal', 'development_plan']),
                  ('gap_deal_state', '=', 'agree_leader'), ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)],
                 args_extended])
            args_extended = expression.OR(
                [[('state', '=', 'in_process'), ('evaluation_type', 'in', ['gap_deal', 'development_plan']),
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
                  '|', ('evaluated_id', '=', self.env.user.employee_id.id),
                  ('evaluator_id', '=', self.env.user.employee_id.id),
                  ('inciso_id', '=', inciso_id), ('operating_unit_id', '=', operating_unit_id)], args_extended])

        return expression.AND([args_extended, args])

    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', required=True, readonly=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', readonly=True)
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador', readonly=True)
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado', readonly=True)
    evaluation_start_date = fields.Date(string='Fecha inicio ciclo evaluación')
    evaluation_end_date = fields.Date(string='Fecha fin ciclo evaluación')
    state = fields.Selection(STATE, string='Estado', readonly=True)
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

    def button_open_evaluation(self):
        ctx = self.env.context.copy()
        ctx.update({'readonly_evaluation': True})
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
               END AS state,
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
               id as evaluation_id
        FROM onsc_desempeno_evaluation
        WHERE year IN (EXTRACT(YEAR FROM CURRENT_DATE), EXTRACT(YEAR FROM CURRENT_DATE) - 1) ) AS main_query)''')
