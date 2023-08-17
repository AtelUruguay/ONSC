# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from odoo import fields, models, api, tools
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluationList(models.Model):
    _name = 'onsc.desempeno.evaluation.list'
    _description = u'Lista de participantes de evaluaciones 360°'

    def _get_domain(self, args):
        if self.user_has_groups('onsc_desempeno.group_desempeno_usuario_gh_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
            args = expression.AND([[('inciso_id', '=', inciso_id), ], args])
        elif self.user_has_groups('onsc_desempeno.group_desempeno_usuario_gh_ue'):
            operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
            args = expression.AND([[('operating_unit_id', '=', operating_unit_id), ], args])
        elif self.user_has_groups('onsc_desempeno.group_desempeno_responsable_uo'):
            department_id = self.env.user.employee_id.job_id.department_id.id
            department_ids = self.env['hr.department'].search(['|',
                                                               ('id', 'child_of', department_id),
                                                               ('id', '=', department_id)]).ids
            args = expression.AND([[('department_id', 'in', department_ids), ], args])

        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluationList, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count,
                                                                access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    name = fields.Char(string='Nombre', compute='_compute_name', store=True)
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
    inciso_id = fields.Many2one(
        "onsc.catalog.inciso",
        string="Inciso",
        related="evaluation_stage_id.inciso_id",
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
    manager_id = fields.Many2one(
        "hr.employee",
        string="Líder",
        compute='_compute_manager_id',
        search='_search_manager_id',
        store=False)
    year = fields.Integer(
        u'Año a evaluar',
        related="evaluation_stage_id.year",
        store=True)

    is_imanager = fields.Boolean(
        string=' Responsable',
        search='_search_is_imanager',
        store=False,
        required=False)

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

    evaluation_generated_line_ids = fields.One2many(
        comodel_name='onsc.desempeno.evaluation.list.line',
        inverse_name='evaluation_list_id',
        context={'active_test': False},
        domain=[('active', '=', False), ('state', '=', 'generated')],
        string='Colaboradores con formularios')

    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    _sql_constraints = [
        ('recordset_uniq', 'unique(department_id,evaluation_stage_id)',
         u'Ya existe una lista de evaluación para esta unidad organizativa y ciclo de evaluación.'),
    ]

    @api.depends('evaluation_stage_id', 'manager_id')
    def _compute_name(self):
        for rec in self:
            rec.name = 'Evaluación: %s, Responsable: %s' % (
                rec.evaluation_stage_id.name,
                rec.manager_id.name)

    def _compute_manager_id(self):
        for rec in self:
            rec.manager_id = rec.department_id.get_first_department_withmanager_in_tree().manager_id.id

    def _search_is_imanager(self, operator, value):
        all_evaluation_list = self.search([])
        evaluation_list_filtered = self.env['onsc.desempeno.evaluation.list']
        for evaluation_list in all_evaluation_list:
            manager_id = evaluation_list.department_id.get_first_department_withmanager_in_tree().manager_id.id
            if manager_id == self.env.user.employee_id.id:
                evaluation_list_filtered |= evaluation_list
        return [('id', 'in', evaluation_list_filtered.ids)]

    def _search_manager_id(self, operator, value):
        all_evaluation_list = self.search([])
        evaluation_list_filtered = self.env['onsc.desempeno.evaluation.list']
        for evaluation_list in all_evaluation_list:
            manager = evaluation_list.department_id.get_first_department_withmanager_in_tree().manager_id
            if isinstance(value, int) and manager.id == value:
                evaluation_list_filtered |= evaluation_list
            elif isinstance(value, str) and value.lower() in manager.display_name.lower():
                evaluation_list_filtered |= evaluation_list
        return [('id', 'in', evaluation_list_filtered.ids)]

    @api.depends('end_date', 'state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            valid_edit = record.state == 'closed' or record.end_date < fields.Date.today() or not record.end_date
            record.should_disable_form_edit = valid_edit

    def button_generate_evaluations(self):
        self.ensure_one()
        lines_evaluated = self.env['onsc.desempeno.evaluation.list.line']
        valid_lines = self.line_ids.filtered(lambda x: x.state != 'generated' and x.is_included)
        with self._cr.savepoint():
            for line in valid_lines:
                try:
                    new_evaluation = self._create_self_evaluation(line)
                    self._create_leader_evaluation(line)
                    if fields.Date.today() <= self.end_date:
                        self._create_environment_definition(line)
                        self._create_collaborator_evaluation(line)
                    line.write({
                        'state': 'generated',
                        'error_log': False,
                        'evaluation_ids': [(6, 0, [new_evaluation.id])]})
                    lines_evaluated |= line
                except Exception as e:
                    line.write({'state': 'error', 'error_log': tools.ustr(e)})
        return lines_evaluated

    # INTELIGENCIA
    def manage_evaluations_lists(self):
        # cerrar las listas que ya pasaron la fecha de cierre
        self.search([('end_date', '<', fields.Date.today())]).write({'state': 'closed'})

        evaluation_stages = self.env['onsc.desempeno.evaluation.stage'].search([
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today()),
        ])
        inlist_evaluation_stage_ids = self.search(
            [('evaluation_stage_id', 'in', evaluation_stages.ids)]).mapped('evaluation_stage_id.id')
        # si ya esta la lista creada para esa UE excluir
        for evaluation_stage in evaluation_stages.filtered(lambda x: x.id not in inlist_evaluation_stage_ids):
            self._create_data(evaluation_stage)
        return True

    def _create_data(self, evaluation_stage):
        Jobs = self.env['hr.job'].suspend_security()
        EvaluationList = self.env['onsc.desempeno.evaluation.list']
        evaluation_lists = self.env['onsc.desempeno.evaluation.list']

        exluded_descriptor1_ids = self.env.company.descriptor1_ids.ids
        jobs = Jobs.search([
            ('department_id.operating_unit_id', '=', evaluation_stage.operating_unit_id.id),
            ('contract_id.legajo_state', 'in', ['active', 'incoming_commission']),
            ('contract_id.descriptor1_id', 'not in', exluded_descriptor1_ids),
            '|',
            ('end_date', '>=', evaluation_stage.start_date),
            ('end_date', '=', False),
        ])
        # Creamos un diccionario con defaultdict para evitar comprobaciones de existencia
        departments_grouped_info = defaultdict(lambda: {'job_ids': set()})
        # departments_responsible_grouped_info = defaultdict(lambda: {'job_ids': set()})
        for job in jobs:
            manager = job.department_id.get_first_department_withmanager_in_tree().manager_id
            parent_manager = job.department_id.parent_id.get_first_department_withmanager_in_tree().manager_id
            eval1 = not (job.department_id.hierarchical_level_id.order == 1
                         and job.department_id.manager_id.id == job.employee_id.id)
            eval2 = job.employee_id.id != manager.id
            if eval1 and eval2:
                departments_grouped_info[job.department_id]['department_id'] = job.department_id
                departments_grouped_info[job.department_id]['job_ids'].add(job)
            elif eval1 and not eval2 and job.department_id.parent_id.id and parent_manager.id != job.employee_id.id:
                # departments_responsible_grouped_info[job.department_id.parent_id]['department_id'] = job.department_id.parent_id
                # departments_responsible_grouped_info[job.department_id.parent_id]['job_ids'].add(job)
                departments_grouped_info[job.department_id.parent_id]['department_id'] = job.department_id.parent_id
                departments_grouped_info[job.department_id.parent_id]['job_ids'].add(job)

        # Convertimos el diccionario de defaultdict a un diccionario estándar
        departments_grouped_info = dict(departments_grouped_info)
        for department, info in departments_grouped_info.items():
            evaluation_vals = {
                'evaluation_stage_id': evaluation_stage.id,
                'department_id': department.id,
            }
            # for department_responsible,info_responsible in departments_responsible_grouped_info.items():
            #     if department_responsible.id == department.id:
            #         info['job_ids'] |= info_responsible['job_ids']
            line_vals = []
            for job in info.get('job_ids', []):
                line_vals.append([0, 0, {
                    'job_id': job.id,
                }])
            evaluation_vals['line_ids'] = line_vals
            evaluation_lists |= EvaluationList.create(evaluation_vals)
        return evaluation_lists

    def _link_jobs(self, jobs):
        for job in jobs:
            self.search([
                ('department_id', '=', job.department_id.id),
                ('state', '=', 'in_progress')]).write({'line_ids': [(0, 0, {'job_id': job.id})]})
        return True

    def _create_self_evaluation(self, data):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()

        evaluation = Evaluation.create({
            'evaluated_id': data.employee_id.id,
            'evaluator_id': data.employee_id.id,
            'evaluation_type': 'self_evaluation',
            'uo_id': data.job_id.department_id.id,
            'inciso_id': data.contract_id.inciso_id.id,
            'operating_unit_id': data.contract_id.operating_unit_id.id,
            'occupation_id': data.contract_id.occupation_id.id,
            'level_id': data.contract_id.occupation_id.level_id.id,
            'general_cycle_id': data.evaluation_list_id.evaluation_stage_id.general_cycle_id.id,
            'evaluation_start_date': data.evaluation_list_id.start_date,
            'evaluation_end_date': data.evaluation_list_id.end_date,
            'state': 'draft',
        })

        # SKILL es la de la nota
        # skill line son las hijas que es puro visual
        for skill in self.env['onsc.desempeno.skill.line'].suspend_security().search(
                [('level_id', '=', evaluation.level_id.id)]).mapped('skill_id'):
            Competency.create({'evaluation_id': evaluation.id,
                               'skill_id': skill.id,
                               # 'display_type': False
                               })
            for skill_line in skill.skill_line_ids:
                Competency.create({'evaluation_id': evaluation.id,
                                   'skill_id': skill.id,
                                   'dimension_id': skill_line.dimension_id.id,
                                   'name': '%s - %s' % (skill_line.dimension_id.name, skill_line.behavior),
                                   'display_type': 'line_note'
                                   })
        return evaluation

    def _create_leader_evaluation(self, data):
        # TODO Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        return True

    def _create_environment_definition(self, data):
        # TODO  Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        return True

    def _create_collaborator_evaluation(self, data):
        # TODO  Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        return True


class ONSCDesempenoEvaluationListLine(models.Model):
    _name = 'onsc.desempeno.evaluation.list.line'
    _description = u'Lista de participantes de evaluaciones 360° - Linea'

    evaluation_list_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list',
        string='Evaluation_list_id',
        ondelete='cascade',
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
    excluded_cause = fields.Text(string='Motivo exclusión')
    error_log = fields.Text(string='Log')
    state = fields.Selection(
        string='Formulario',
        selection=[('stand', 'Pendiente'),
                   ('error', 'Error'),
                   ('generated', 'Generado')],
        required=True,
        default='stand')
    active = fields.Boolean(
        string='',
        compute='_compute_active',
        store=True)

    evaluation_ids = fields.Many2many(
        'onsc.desempeno.evaluation',
        'desempeno_evaluation_list_line_evaluation', 'line_id', 'evaluation_id',
        string='Evaluaciones',
        readonly=True)

    @api.onchange('is_included')
    def onchange_is_included(self):
        self.excluded_cause = ''

    @api.depends('employee_id')
    def _compute_legajo_id(self):
        Legajo = self.env['onsc.legajo']
        for record in self:
            record.legajo_id = Legajo.search([('employee_id', '=', record.employee_id.id)], limit=1)

    @api.depends('job_id.end_date', 'state')
    def _compute_active(self):
        for record in self:
            job_active = record.job_id.end_date is False or record.job_id.end_date >= fields.Date.today()
            record.active = job_active and record.state != 'generated'

    def button_open_current_contract(self):
        action = self.sudo().env.ref('onsc_legajo.onsc_legajo_one_hr_contract_action').read()[0]
        action.update({'res_id': self.contract_id.id})
        return action
