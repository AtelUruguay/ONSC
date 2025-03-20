# -*- coding: utf-8 -*-
import logging
import random
from collections import defaultdict

from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import ValidationError
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
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluationList, self)._search(args, offset=offset, limit=limit, order=order,
                                                                count=count,
                                                                access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
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
    manager_uo_id = fields.Many2one(
        "hr.department",
        string="UO del Líder",
        compute='_compute_manager_id',
        store=False)
    # LUEGO DE CERRADA LA LISTA LOS DATOS DEL RESPONSABLE QUEDAN FIJOS
    fixed_manager_id = fields.Many2one(
        "hr.employee",
        string="Líder al cierre de la lista")
    fixed_manager_uo_id = fields.Many2one(
        "hr.department",
        string="UO del Líder al cierre de la lista")
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
    is_line_availables = fields.Boolean(
        string='¿Hay colaboradores por generar evaluación?',
        compute='_compute_is_line_availables'
    )

    is_line_generated_availables = fields.Boolean(
        string='¿Hay colaboradores con evaluaciones generadas?',
        compute='_compute_is_line_availables'
    )

    search_employee_inlines = fields.Many2one(
        "hr.employee",
        string='Evaluado',
        search='_search_employee_inlines',
        store=False)

    _sql_constraints = [
        ('recordset_uniq', 'unique(department_id,evaluation_stage_id)',
         u'Ya existe una lista de evaluación para esta unidad organizativa y ciclo de evaluación.'),
    ]

    def _search_employee_inlines(self, operator, operand):
        if isinstance(operand, int):
            args = [('employee_id', operator, operand)]
        else:
            args = [('employee_id.name', operator, operand)]
        lines = self.env['onsc.desempeno.evaluation.list.line'].with_context(active_test=False).search(args)
        return [('id', 'in', lines.mapped('evaluation_list_id').ids)]

    @api.depends('evaluation_stage_id', 'department_id')
    def _compute_name(self):
        for rec in self:
            rec.name = 'Evaluación: %s, UO: %s' % (
                rec.evaluation_stage_id.name,
                rec.department_id.name)

    @api.depends('line_ids')
    def _compute_is_line_availables(self):
        for rec in self:
            rec.is_line_availables = len(rec.line_ids) > 0
            rec.is_line_generated_availables = len(rec.evaluation_generated_line_ids) > 0

    def _compute_manager_id(self):
        for rec in self:
            if rec.state == 'closed':
                # si esta cerrada la lista toma los valores fijos de responsables almacenados al cerrar
                rec.manager_id = rec.fixed_manager_id.id
                rec.manager_uo_id = rec.fixed_manager_uo_id.id
            else:
                manager_department = rec.department_id.get_first_department_withmanager_in_tree()
                rec.manager_id = manager_department.manager_id.id
                rec.manager_uo_id = manager_department.id

    def _search_is_imanager(self, operator, value):
        all_evaluation_list = self.search([])
        evaluation_list_filtered = self.env['onsc.desempeno.evaluation.list']
        for evaluation_list in all_evaluation_list:
            if evaluation_list.state == 'closed':
                manager_id = evaluation_list.fixed_manager_id
            else:
                manager_id = evaluation_list.department_id.get_first_department_withmanager_in_tree().manager_id.id
            if manager_id == self.env.user.employee_id.id:
                evaluation_list_filtered |= evaluation_list
        return [('id', 'in', evaluation_list_filtered.ids)]

    def _search_manager_id(self, operator, value):
        all_evaluation_list = self.search([])
        evaluation_list_filtered = self.env['onsc.desempeno.evaluation.list']
        for evaluation_list in all_evaluation_list:
            if evaluation_list.state == 'closed':
                manager = evaluation_list.fixed_manager_id
            else:
                manager = evaluation_list.department_id.get_first_department_withmanager_in_tree().manager_id
            if isinstance(value, int) and manager.id == value:
                evaluation_list_filtered |= evaluation_list
            elif manager and isinstance(value, str) and value.lower() in manager.display_name.lower():
                evaluation_list_filtered |= evaluation_list
        return [('id', 'in', evaluation_list_filtered.ids)]

    @api.depends('end_date', 'state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            condition = record.evaluation_stage_id.general_cycle_id.end_date_max < fields.Date.today()
            valid_edit = record.state == 'closed' or condition or not record.end_date
            record.should_disable_form_edit = valid_edit

    def button_generate_evaluations(self):
        self.ensure_one()
        partners_to_notify = self.manager_id.partner_id
        lines_evaluated = self.env['onsc.desempeno.evaluation.list.line']
        valid_lines = self.line_ids.filtered(lambda x: x.state != 'generated' and x.is_included)
        with self._cr.savepoint():
            if fields.Date.today() < self.end_date and len(valid_lines) > 0:
                self.suspend_security()._create_collaborator_evaluation()
            for line in valid_lines:
                try:
                    _evaluation_ids = []
                    if fields.Date.today() < self.evaluation_stage_id.general_cycle_id.end_date_max:
                        new_evaluation = self.suspend_security()._create_self_evaluation(line)
                        leader_evaluation = self.suspend_security()._create_leader_evaluation(line)
                        _evaluation_ids.extend([(4, new_evaluation.id), (4, leader_evaluation.id)])
                        if fields.Date.today() >= self.end_date and self.evaluation_stage_id.closed_stage:
                            gap_deal = self.suspend_security()._create_gap_deal(leader_evaluation)
                            _evaluation_ids.extend([(4, gap_deal.id)])
                    if fields.Date.today() < self.end_date and fields.Date.today() <= self.end_date_environment:
                        env_def_evaluation = self.suspend_security()._create_environment_definition(line)
                        _evaluation_ids.append((4, env_def_evaluation.id))

                    if len(_evaluation_ids) > 0:
                        line.suspend_security().write({
                            'state': 'generated',
                            'error_log': False,
                            'evaluation_create_date': fields.Date.today(),
                            'evaluation_ids': _evaluation_ids
                        })
                        lines_evaluated |= line
                    partners_to_notify |= line.employee_id.partner_id
                except Exception as e:
                    line.write({
                        'state': 'error',
                        'error_log': 'Error al generar formulario contacte al administrador. %s' % (tools.ustr(e))})
        self.with_context(partners_to_notify=partners_to_notify)._send_generated_form_notification()
        return lines_evaluated

    # INTELIGENCIA
    def manage_evaluations_lists(self):
        # cerrar las listas que ya pasaron la fecha de cierre y fijar responsable
        lists_toclose = self.search([
            ('state', '!=', 'closed'),
            ('evaluation_stage_id.general_cycle_id.end_date_max', '<', fields.Date.today())])
        for list_toclose in lists_toclose:
            list_toclose.write({
                'fixed_manager_id': list_toclose.manager_id.id,
                'fixed_manager_uo_id': list_toclose.manager_uo_id.id,
            })
        lists_toclose.write({'state': 'closed'})

        evaluation_stages = self.env['onsc.desempeno.evaluation.stage'].search([
            ('start_date', '<=', fields.Date.today()),
            ('end_date', '>=', fields.Date.today()),
            ('closed_stage', '=', False)
        ])
        for evaluation_stage in evaluation_stages:
            department_inlist = self._get_evaluation_list_departments(evaluation_stage)
            self._create_data(evaluation_stage, department_inlist)
        return True

    def _create_data(self, evaluation_stage, department_inlist):
        Jobs = self.env['hr.job'].suspend_security()
        EvaluationList = self.env['onsc.desempeno.evaluation.list']
        evaluation_lists = self.env['onsc.desempeno.evaluation.list']

        exluded_descriptor1_ids = self.env.company.descriptor1_ids.ids

        self._cr.execute(
            """SELECT DISTINCT current_job_id FROM onsc_desempeno_evaluation WHERE current_job_id IS NOT NULL""")
        result = self._cr.fetchall()
        evaluation_current_job_ids = [value[0] for value in result]

        jobs = Jobs.search([
            ('id', 'not in', evaluation_current_job_ids),
            ('department_id.id', 'not in', department_inlist.ids),
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
            elif eval1 and not eval2 and job.department_id.parent_id.id and \
                    parent_manager.id != job.employee_id.id and \
                    job.department_id.parent_id.id not in department_inlist.ids:
                departments_grouped_info[job.department_id.parent_id]['department_id'] = job.department_id.parent_id
                departments_grouped_info[job.department_id.parent_id]['job_ids'].add(job)

        # Convertimos el diccionario de defaultdict a un diccionario estándar
        departments_grouped_info = dict(departments_grouped_info)
        for department, info in departments_grouped_info.items():
            evaluation_vals = {
                'evaluation_stage_id': evaluation_stage.id,
                'department_id': department.id,
            }
            line_vals = []
            for job in info.get('job_ids', []):
                line_vals.append([0, 0, {
                    'job_id': job.id,
                }])
            evaluation_vals['line_ids'] = line_vals
            evaluation_lists |= EvaluationList.create(evaluation_vals)

        for evaluation_list in EvaluationList.search([
            ('evaluation_stage_id', '=', evaluation_stage.id),
            ('state', '=', 'in_progress'),
        ]):
            if not evaluation_list.manager_uo_id:
                continue
            manage_job = Jobs.get_management_job_from_department(evaluation_list.manager_uo_id)
            is_manager_job_in_other_autoevaluations = self.is_manager_job_in_other_autoevaluations(
                manage_job,
                evaluation_stage
            )
            if is_manager_job_in_other_autoevaluations:
                continue

            parent_manager_department = evaluation_list.manager_uo_id.parent_id
            parent_evaluation_list = EvaluationList.search([
                ('operating_unit_id', '=', evaluation_list.operating_unit_id.id),
                ('department_id', '=', parent_manager_department.id),
                ('evaluation_stage_id', '=', evaluation_stage.id),
                ('state', '=', 'in_progress')
            ], limit=1)

            if parent_manager_department and not parent_evaluation_list:
                contract_state_valid = manage_job and manage_job.contract_id.legajo_state in [
                    'active',
                    'incoming_commission'
                ]
                contract_not_excluded = manage_job and manage_job.contract_id.descriptor1_id not in exluded_descriptor1_ids

                if manage_job and contract_state_valid and contract_not_excluded:
                    evaluation_vals = {
                        'evaluation_stage_id': evaluation_stage.id,
                        'department_id': parent_manager_department.id,
                        'line_ids': [(0, 0, {'job_id': manage_job.id})]
                    }
                    evaluation_lists |= EvaluationList.create(evaluation_vals)
            elif manage_job and parent_evaluation_list and not parent_evaluation_list.with_context(active_test=False).line_ids.filtered(
                    lambda x: x.employee_id.id == evaluation_list.manager_id.id):
                parent_evaluation_list.write({'line_ids': [(0, 0, {'job_id': manage_job.id})]})

        return evaluation_lists

    def is_manager_job_in_other_autoevaluations(self, manage_job, evaluation_stage):
        """

        :param manage_job: Recordset: hr.job Puesto del responsable
        :param evaluation_stage: Recorder onsc.desempeno.evaluation.stage Ciclo 390
        :return: Si ese puesto ya tiene autoevaluaciones no canceladas para ese Ciclo360
        """
        self._cr.execute("""SELECT COUNT(id) FROM onsc_desempeno_evaluation WHERE
                                                current_job_id=%s AND
                                                evaluation_type='%s' AND
                                                evaluation_stage_id=%s AND
                                                state <> '%s'
                                """ % (manage_job.id, 'self_evaluation', evaluation_stage.id, 'canceled'))
        result = self._cr.fetchone()
        return result[0] > 0

    def _get_evaluation_list_departments(self, evaluation_stages):
        """
        DEVUELVE UOS QUE YA TIENEN LISTA GENERADO PARA ESA 360
        :param evaluation_stage: Instances of onsc.desempeno.evaluation.stage
        """
        return self.search([('evaluation_stage_id', 'in', evaluation_stages.ids)]).mapped('department_id')

    def _link_jobs(self, jobs):
        for job in jobs:
            self.search([
                ('department_id', '=', job.department_id.id),
                ('state', '=', 'in_progress')]).write({'line_ids': [(0, 0, {'job_id': job.id})]})
        return True

    def _create_self_evaluation(self, data):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        hierachy_manager_id = data.job_id.department_id.get_first_department_withmanager_in_tree().manager_id.id
        is_manager = hierachy_manager_id == data.employee_id.id
        level_id = Level.suspend_security().search(
            [('hierarchical_level_id', '=', data.job_id.department_id.hierarchical_level_id.id),
             ('is_uo_manager', '=', is_manager)]).mapped("level_id")
        if not level_id:
            raise ValidationError(
                _(u"No existe nivel configurado para la combinación de nivel jerárquico y responsable UO"))
        skills = self.env['onsc.desempeno.skill.line'].suspend_security().search(
            [('level_id', '=', level_id.id)]).mapped('skill_id').filtered(lambda r: r.active)
        if not skills:
            raise ValidationError(_(u"No se ha encontrado ninguna competencia activa"))

        evaluation = Evaluation.create({
            'current_job_id': data.job_id.id,
            'evaluator_current_job_id': data.job_id.id,
            'evaluation_list_id': data.evaluation_list_id.id,
            'evaluated_id': data.employee_id.id,
            'evaluator_id': data.employee_id.id,
            'list_manager_id': data.evaluation_list_id.manager_id.id,
            'evaluator_uo_id': data.evaluation_list_id.manager_uo_id.id,
            'evaluation_type': 'self_evaluation',
            'uo_id': data.job_id.department_id.id,
            'inciso_id': data.contract_id.inciso_id.id,
            'operating_unit_id': data.contract_id.operating_unit_id.id,
            'level_id': level_id.id,
            'evaluation_stage_id': data.evaluation_list_id.evaluation_stage_id.id,
            'general_cycle_id': data.evaluation_list_id.evaluation_stage_id.general_cycle_id.id,
            'state': 'draft',
        })
        Competency.set_competencies( skills,evaluation)

        # for skill in skills:
        #     Competency.create({'evaluation_id': evaluation.id,
        #                        'skill_id': skill.id,
        #                        'skill_line_ids': [(6, 0, skill.skill_line_ids.filtered(
        #                            lambda r: r.level_id.id == evaluation.level_id.id).ids)]
        #                        })

        return evaluation

    def _create_leader_evaluation(self, data):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        Job = self.env['hr.job'].sudo()
        hierachy_manager_id = data.job_id.department_id.get_first_department_withmanager_in_tree().manager_id.id
        is_manager = hierachy_manager_id == data.employee_id.id
        level_id = Level.suspend_security().search(
            [('hierarchical_level_id', '=', data.job_id.department_id.hierarchical_level_id.id),
             ('is_uo_manager', '=', is_manager)]).mapped("level_id")
        if not level_id:
            raise ValidationError(
                _(u"No existe nivel configurado para la combinación de nivel jerárquico y responsable UO"))
        skills = self.env['onsc.desempeno.skill.line'].suspend_security().search(
            [('level_id', '=', level_id.id)]).mapped('skill_id').filtered(lambda r: r.active)
        if not skills:
            raise ValidationError(_(u"No se ha encontrado ninguna competencia activa"))

        evaluator_current_job_id = Job.search([
            ('employee_id', '=', self.manager_id.id),
            ('department_id', '=', data.evaluation_list_id.manager_uo_id.id),
            '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())
        ], limit=1).id

        evaluation = Evaluation.create({
            'current_job_id': data.job_id.id,
            'evaluator_current_job_id': evaluator_current_job_id,
            'evaluation_list_id': data.evaluation_list_id.id,
            'evaluated_id': data.employee_id.id,
            'evaluator_id': self.manager_id.id,
            'list_manager_id': data.evaluation_list_id.manager_id.id,
            'evaluator_uo_id': data.evaluation_list_id.manager_uo_id.id,
            'evaluation_type': 'leader_evaluation',
            'uo_id': data.job_id.department_id.id,
            'inciso_id': data.contract_id.inciso_id.id,
            'operating_unit_id': data.contract_id.operating_unit_id.id,
            'level_id': level_id.id,
            'evaluation_stage_id': data.evaluation_list_id.evaluation_stage_id.id,
            'general_cycle_id': data.evaluation_list_id.evaluation_stage_id.general_cycle_id.id,
            'state': 'draft',
        })
        Competency.set_competencies(skills, evaluation)
        # for skill in skills:
        #     Competency.create({'evaluation_id': evaluation.id,
        #                        'skill_id': skill.id,
        #                        'skill_line_ids': [(6, 0, skill.skill_line_ids.filtered(
        #                            lambda r: r.level_id.id == evaluation.level_id.id).ids)]
        #                        })

        return evaluation

    def _create_environment_definition(self, data):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        hierachy_manager_id = data.job_id.department_id.get_first_department_withmanager_in_tree().manager_id.id
        is_manager = hierachy_manager_id == data.employee_id.id
        level_id = Level.suspend_security().search(
            [('hierarchical_level_id', '=', data.job_id.department_id.hierarchical_level_id.id),
             ('is_uo_manager', '=', is_manager)]).mapped("level_id")
        if not level_id:
            raise ValidationError(
                _(u"No existe nivel configurado para la combinación de nivel jerárquico y responsable UO"))
        skills = self.env['onsc.desempeno.skill.line'].suspend_security().search(
            [('level_id', '=', level_id.id)]).mapped('skill_id').filtered(lambda r: r.active)
        if not skills:
            raise ValidationError(_(u"No se ha encontrado ninguna competencia activa"))

        evaluation = Evaluation.create({
            'current_job_id': data.job_id.id,
            'evaluator_current_job_id': data.job_id.id,
            'evaluation_list_id': data.evaluation_list_id.id,
            'evaluated_id': data.employee_id.id,
            'evaluator_id': data.employee_id.id,
            'list_manager_id': data.evaluation_list_id.manager_id.id,
            'evaluator_uo_id': data.evaluation_list_id.manager_uo_id.id,
            'evaluation_type': 'environment_definition',
            'uo_id': data.job_id.department_id.id,
            'inciso_id': data.contract_id.inciso_id.id,
            'operating_unit_id': data.contract_id.operating_unit_id.id,
            'level_id': level_id.id,
            'evaluation_stage_id': data.evaluation_list_id.evaluation_stage_id.id,
            'general_cycle_id': data.evaluation_list_id.evaluation_stage_id.general_cycle_id.id,
            'state': 'draft',
        })

        return evaluation

    def _create_collaborator_evaluation(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        Job = self.env['hr.job'].sudo()
        valid_lines = self.line_ids.filtered(lambda x: x.state != 'generated' and x.is_included)
        generated_evaluations = self.evaluation_generated_line_ids.mapped('evaluation_ids')
        generated_evaluations_collaborator_qty = len(
            generated_evaluations.filtered(lambda x: x.evaluation_type == 'collaborator'))

        if not self.is_manager_available_tocreate_evaluations_toitself():
            return True
        if len(valid_lines) == 1 and generated_evaluations_collaborator_qty == 0:
            if self.end_date_environment >= fields.Date.today():
                self._create_environment_evaluation(valid_lines)
            return True
        if generated_evaluations_collaborator_qty < 4:
            for data in self._get_records_random(valid_lines, generated_evaluations_collaborator_qty):
                level_id = Level.suspend_security().search(
                    [('hierarchical_level_id', '=', self.manager_uo_id.hierarchical_level_id.id),
                     ('is_uo_manager', '=', True)]).mapped("level_id")
                if not level_id:
                    raise ValidationError(
                        _(u"No existe nivel configurado para la combinación de nivel jerárquico y responsable UO"))
                skills = self.env['onsc.desempeno.skill.line'].suspend_security().search(
                    [('level_id', '=', level_id.id)]).mapped('skill_id').filtered(lambda r: r.active)
                if not skills:
                    raise ValidationError(_(u"No se ha encontrado ninguna competencia activa"))

                current_job_id = Job.search([
                    ('employee_id', '=', self.manager_id.id),
                    ('department_id', '=', data.evaluation_list_id.manager_uo_id.id),
                    '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())
                ], limit=1).id

                evaluation = Evaluation.create({
                    'evaluator_current_job_id': data.job_id.id,
                    'current_job_id': current_job_id,
                    'evaluation_list_id': data.evaluation_list_id.id,
                    'evaluated_id': self.manager_id.id,
                    'evaluator_id': data.employee_id.id,
                    'list_manager_id': data.evaluation_list_id.manager_id.id,
                    'evaluator_uo_id': data.evaluation_list_id.manager_uo_id.id,
                    'evaluation_type': 'collaborator',
                    'uo_id': self.manager_uo_id.id,
                    'inciso_id': data.contract_id.inciso_id.id,
                    'operating_unit_id': data.contract_id.operating_unit_id.id,
                    'level_id': level_id.id,
                    'evaluation_stage_id': self.evaluation_stage_id.id,
                    'general_cycle_id': self.evaluation_stage_id.general_cycle_id.id,
                    'state': 'draft',
                })
                Competency.set_competencies(skills, evaluation)
                # for skill in skills:
                #     Competency.create({'evaluation_id': evaluation.id,
                #                        'skill_id': skill.id,
                #                        'skill_line_ids': [(6, 0, skill.skill_line_ids.filtered(
                #                            lambda r: r.level_id.id == evaluation.level_id.id).ids)]
                #                        })
                data.write({'evaluation_ids': [(4, evaluation.id)]})
        return True

    def is_manager_available_tocreate_evaluations_toitself(self):
        Job = self.env['hr.job'].suspend_security()
        excluded_descriptor1_ids = self.env.company.descriptor1_ids.ids
        # OBTENIENDO PUESTO ACTIVO PARA EL MANAGER EN LA ESTRUCTURA JERARQUICA DE LA LISTA
        job = Job.search([
            ('department_id', '=', self.manager_uo_id.id),
            ('employee_id', '=', self.manager_id.id),
            '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())
        ], limit=1)
        # SI CONTRATO EN DESCRIPTORES EXCLUIDOS ENTONCES NO DISPONIBLE
        if job.contract_id.descriptor1_id.id in excluded_descriptor1_ids:
            return False
        # SI UO NIVEL 1 ENTONCES NO DISPONIBLE
        if job.department_id.hierarchical_level_id.order == 1:
            return False
        return True

    def _create_environment_evaluation(self, data):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        Job = self.env['hr.job'].sudo()

        level_id = Level.suspend_security().search(
            [('hierarchical_level_id', '=', self.manager_uo_id.hierarchical_level_id.id),
             ('is_uo_manager', '=', True)]).mapped("level_id")
        if not level_id:
            raise ValidationError(
                _(u"No existe nivel configurado para la combinación de nivel jerárquico y responsable UO"))
        skills = self.env['onsc.desempeno.skill.line'].suspend_security().search(
            [('level_id', '=', level_id.id)]).mapped('skill_id').filtered(lambda r: r.active)
        if not skills:
            raise ValidationError(_(u"No se ha encontrado ninguna competencia activa"))

        current_job_id = Job.search([
            ('employee_id', '=', self.manager_id.id),
            ('department_id', '=', data.evaluation_list_id.manager_uo_id.id),
            '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())
        ], limit=1).id

        evaluation = Evaluation.create({
            'evaluator_current_job_id': data.job_id.id,
            'current_job_id': current_job_id,
            'evaluation_list_id': data.evaluation_list_id.id,
            'evaluated_id': self.manager_id.id,
            'evaluator_id': data.employee_id.id,
            'evaluator_uo_id': data.evaluation_list_id.manager_uo_id.id,
            'list_manager_id': data.evaluation_list_id.manager_id.id,
            'evaluation_type': 'environment_evaluation',
            'uo_id': data.job_id.department_id.id,
            'inciso_id': data.contract_id.inciso_id.id,
            'operating_unit_id': data.contract_id.operating_unit_id.id,
            'level_id': level_id.id,
            'evaluation_stage_id': self.evaluation_stage_id.id,
            'general_cycle_id': self.evaluation_stage_id.general_cycle_id.id,
            'state': 'draft',
        })
        Competency.set_competencies(skills, evaluation)
        # for skill in skills:
        #     Competency.create({'evaluation_id': evaluation.id,
        #                        'skill_id': skill.id,
        #                        'skill_line_ids': [(6, 0, skill.skill_line_ids.filtered(
        #                            lambda r: r.level_id.id == evaluation.level_id.id).ids)]
        #                        })
        data.write({'evaluation_ids': [(4, evaluation.id)]})
        return True

    def _create_gap_deal(self, record):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Job = self.env['hr.job'].sudo()
        partners_to_notify = self.env["res.partner"]
        evaluation = record.copy_data()
        evaluation[0]["evaluation_type"] = "gap_deal"
        evaluation[0]["current_job_id"] = record.current_job_id.id
        evaluation[0]["evaluator_current_job_id"] = record.evaluator_current_job_id.id
        if record.current_job_id:
            _department_id = record.current_job_id.department_id
            if _department_id.manager_id == record.current_job_id.employee_id:
                manager_department = _department_id.get_first_department_withmanager_in_tree(ignore_first_step=True)
            else:
                manager_department = _department_id.get_first_department_withmanager_in_tree()
            evaluator_current_job_id = Job.search([
                ('employee_id', '=', manager_department.manager_id.id),
                ('department_id', '=', manager_department.id),
                '|', ('end_date', '=', False), ('end_date', '>=', fields.Date.today())
            ], limit=1).id

            # ACTUALIZANDO INFO DEL EVALUADOR
            evaluation[0]["evaluator_current_job_id"] = evaluator_current_job_id
            evaluation[0]["evaluator_id"] = manager_department.manager_id.id
            evaluation[0]["evaluator_uo_id"] = manager_department.id

            evaluation[0]["uo_id"] = record.current_job_id.department_id.id
        gap_deal = Evaluation.with_context(gap_deal=True).create(evaluation)


        for competency in record.evaluation_competency_ids:
            Competency.set_competencies(competency.skill_id.skill_line_ids,evaluation, gap_deal.id)
            # Competency.create({'gap_deal_id': gap_deal.id,
            #                    'skill_id': competency.skill_id.id,
            #                    'skill_line_ids': [(6, 0, competency.skill_id.skill_line_ids.filtered(
            #                        lambda r: r.level_id.id == record.level_id.id).ids)]
            #                    })

        partners_to_notify |= record.evaluated_id.partner_id
        partners_to_notify |= record.evaluator_id.partner_id

        self.with_context(partners_to_notify=partners_to_notify)._send_gap_deal_notification()

        return gap_deal

    def _action_desempeno_evaluation_list(self):
        if self.user_has_groups(
                'onsc_desempeno.group_desempeno_usuario_gh_inciso,onsc_desempeno.group_desempeno_usuario_gh_ue'):
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_list_nofilter_is_imanager_action')
        else:
            action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_list_action')
        return action.read()[0]

    def _get_records_random(self, records, generated):
        qty_to_take = 4 - generated
        if qty_to_take >= len(records):
            records_random = records
        else:
            records_random = random.sample(records, qty_to_take)
        return records_random

    def _send_gap_deal_notification(self):
        generated_form_email_template_id = self.env.ref('onsc_desempeno.email_template_start_stage_2_form')
        generated_form_email_template_id.send_mail(self.evaluation_stage_id.id, force_send=True)

    def _send_generated_form_notification(self):
        generated_form_email_template_id = self.env.ref('onsc_desempeno.email_template_generated_form')
        generated_form_email_template_id.send_mail(self.id, force_send=True)

    def get_followers_mails(self):
        return self._context.get('partners_to_notify').get_onsc_mails()

    def get_start_date(self):
        return fields.Datetime.today().strftime('%d/%m/%Y')

    def fix_25_8_upload_jobs_to_evaluation_lists(self):
        exluded_descriptor1_ids = self.env.company.descriptor1_ids.ids

        jobs_inlist_ids = self.line_ids.mapped('job_id').ids
        jobs_toadd_inlist_ids = self.env['hr.job'].sudo().search([
            ('department_id', '=', self.department_id.id),
            ('is_uo_manager', '=', False),
            ('id', 'not in', jobs_inlist_ids),
            # base args to find the correct jobs like manage evaluation lists
            ('contract_id.legajo_state', 'in', ['active', 'incoming_commission']),
            ('contract_id.descriptor1_id', 'not in', exluded_descriptor1_ids),
            '|',
            ('end_date', '>=', fields.Date.today()),
            ('end_date', '=', False),
        ]).ids
        new_data = []
        for jobs_toadd_inlist_id in jobs_toadd_inlist_ids:
            new_data.append(Command.create({'job_id': jobs_toadd_inlist_id}))
        self.sudo().write({
            'line_ids': new_data
        })

    def fix_25_8_upload_manager_to_parent_evaluation_list(self):
        exluded_descriptor1_ids = self.env.company.descriptor1_ids.ids

        parent_department = self.department_id.parent_id
        parent_list = self.search([
            ('department_id', '=', parent_department.id)
        ])
        if parent_list:
            jobs_toadd_inlist_ids = self.env['hr.job'].sudo().search([
                ('employee_id', '=', self.manager_id.id),
                ('department_id', '=', self.department_id.id),
                ('is_uo_manager', '=', True),
                # base args to find the correct jobs like manage evaluation lists
                ('contract_id.legajo_state', 'in', ['active', 'incoming_commission']),
                ('contract_id.descriptor1_id', 'not in', exluded_descriptor1_ids),
                '|',
                ('end_date', '>=', fields.Date.today()),
                ('end_date', '=', False),
            ]).ids
            new_data = []
            for jobs_toadd_inlist_id in jobs_toadd_inlist_ids:
                if jobs_toadd_inlist_id not in parent_list.line_ids.mapped('job_id').ids:
                    new_data.append(Command.create({'job_id': jobs_toadd_inlist_id}))
            parent_list.sudo().write({
                'line_ids': new_data
            })


class ONSCDesempenoEvaluationListLine(models.Model):
    _name = 'onsc.desempeno.evaluation.list.line'
    _description = u'Lista de participantes de evaluaciones 360° - Linea'

    evaluation_list_id = fields.Many2one(
        comodel_name='onsc.desempeno.evaluation.list',
        string='Lista de participantes',
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

    evaluation_create_date = fields.Date(
        string=u'Fecha de generación',
        index=True,
        readonly=True)

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
