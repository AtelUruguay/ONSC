# -*- coding: utf-8 -*-
from collections import defaultdict

import logging

from odoo import fields, models, api


_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluationList(models.Model):
    _name = 'onsc.desempeno.evaluation.list'
    _description = u'Lista de participantes de evaluaciones 360°'

    evaluation_stage_id = fields.Many2one(
        'onsc.desempeno.evaluation.stage',
        string=u'Evaluación 360',
        required=True,
        index=True)
    start_date = fields.Date(
        string=u'Fecha inicio ciclo de evaluación',
        related='evaluation_stage_id.start_date',
        store=True)
    end_date = fields.Date(
        string=u'Fecha fin ciclo de evaluación',
        related='evaluation_stage_id.end_date',
        store=True)
    end_date_environment = fields.Date(
        string=u'Fecha fin def. entorno',
        related='evaluation_stage_id.end_date_environment',
        store=True)
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora",
        related='evaluation_stage_id.operating_unit_id',
        store=True)
    department_id = fields.Many2one(
        "hr.department",
        string="Unidad organizativa",
        required=True,
        index=True)
    manager_id = fields.Many2one("hr.employee", string="Líder", required=True, index=True)
    state = fields.Selection(
        string='Formulario',
        selection=[('in_progress', 'En proceso'),
                   ('closed', 'Finalizada')],
        required=True,
        default='in_progress')

    line_ids = fields.One2many(
        comodel_name='onsc.desempeno.evaluation.list.line',
        inverse_name='evaluation_list_id',
        string='Colaboradores')


class ONSCDesempenoEvaluationListLine(models.Model):
    _name = 'onsc.desempeno.evaluation.list.line'
    _description = u'Lista de participantes de evaluaciones 360° - Linea'

    evaluation_list_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list',
        string='Evaluation_list_id',
        required=True)
    job_id = fields.Many2one(
        "hr.job",
        string="Puesto",
        required=True,
        index=True)
    contract_id = fields.Many2one(
        "hr.contract",
        string="Contrato",
        related='job_id.contract_id',
        store=True,
        index=True)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Evaluado",
        related='job_id.employee_id',
        store=True,
        index=True)
    legajo_id = fields.Many2one(
        "onsc.legajo",
        string="Legajo",
        compute='_compute_legajo_id',
        store=True,
        index=True)

    regime_id = fields.Many2one(
        'onsc.legajo.regime',
        string='Régimen',
        related='contract_id.regime_id',
        store=True, )
    contract_date_start = fields.Date(
        string='Fecha del último vínculo vigente',
        related='contract_id.date_start',
        store=True)

    is_included = fields.Boolean(string='Incluir en el ciclo', default=True)
    excluded_cause = fields.Char(
        string='Motivo exclusión',
        required=False)
    state = fields.Selection(
        string='Formulario',
        selection=[('stand', 'Pendiente'),
                   ('error', 'Error'),
                   ('generated', 'Generado')],
        required=True,
        default='stand')

    @api.depends('employee_id')
    def _compute_legajo_id(self):
        Legajo = self.env['onsc.legajo']
        for record in self:
            record.legajo_id = Legajo.search([('employee_id', '=', record.employee_id.id)], limit=1)

    # INTELIGENCIA
    def set_evaluation_list(self):
        evaluation_stages = self.env['onsc.desempeno.evaluation.stage'].search([
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today()),
        ])
        inlist_evaluation_stage_ids = self.search(
            [('evaluation_stage_id', 'in', evaluation_stages.ids)].mapped('evaluation_stage_id.id'))
        # si ya esta la lista creada para esa UE excluir
        for evaluation_stage in evaluation_stages.filtered(lambda x: x.id not in inlist_evaluation_stage_ids):
            evaluation_lists = self._create_data(evaluation_stage)
            a = 5


    def _create_data(self, evaluation_stage):
        Jobs = self.env['hr.job'].suspend_security()
        EvaluationList = self.env['onsc.desempeno.evaluation.list']
        evaluation_lists = self.env['onsc.desempeno.evaluation.list']

        exluded_descriptor1_ids = self.env.company.descriptor1_ids.ids
        jobs = Jobs.search([
            ('department_id.hierarchical_level_id.order', '=', 1),
            ('department_id.operating_unit_id', '=', evaluation_stage.operating_unit_id.id),
            ('contract_id.legajo_state', 'in', ['active', 'incoming_commission']),
            ('descriptor1_id', 'not in', exluded_descriptor1_ids),
            '|',
            ('end_date', '>=', evaluation_stage.start_date),
            ('end_date', '=', False),
        ])
        # Creamos un diccionario con defaultdict para evitar comprobaciones de existencia
        departments_grouped_info = defaultdict(lambda: {'job_ids': set()})
        for job in jobs:
            manager = job.department_id.get_first_department_withmanager_in_tree().manager_id
            departments_grouped_info[job.department_id]['department_id'] = job.department_id
            departments_grouped_info[job.department_id]['manager_id'] = manager
            departments_grouped_info[job.department_id]['job_ids'].add(job)

        # Convertimos el diccionario de defaultdict a un diccionario estándar
        departments_grouped_info = dict(departments_grouped_info)
        for department, info in departments_grouped_info.items():
            evaluation_vals = [0, 0, {
                'evaluation_stage_id': evaluation_stage.id,
                'department_id': department.id,
                'manager_id': info.get('manager_id', self.env['hr.employee']).id,
            }]
            line_vals = []
            for job in info.get('job_ids', []):
                line_vals.append([0, 0, {
                    'job_id': job.id,
                }])
            evaluation_vals[2]['line_ids'] = line_vals
            evaluation_lists |= EvaluationList.create(evaluation_vals)
        return evaluation_lists

