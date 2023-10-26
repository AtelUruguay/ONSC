# -*- coding: utf-8 -*-
import logging
import json

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_definition', 'Definición de entorno'),
    ('gap_deal', 'Acuerdo de Brecha'),

]

STATE = [
    ('draft', 'Borrador'),
    ('in_process', 'En Proceso'),
    ('completed', 'Completado'),
    ('finished', 'Finalizado'),
    ('uncompleted', 'Sin Finalizar'),
    ('canceled', 'Cancelado')
]


class ONSCDesempenoEvaluation(models.Model):
    _name = 'onsc.desempeno.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Evaluación'

    def _is_group_admin_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso')

    def _is_group_admin_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue')

    def _is_group_usuario_evaluacion(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_usuario_evaluacion')

    def _is_group_responsable_uo(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_responsable_uo')

    def _is_group_usuario_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_usuario_gh_inciso')

    def _is_group_usuario_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_usuario_gh_ue')

    def _get_domain(self, args):
        if self._context.get('self_evaluation'):
            args = self._get_domain_evaluation(args, 'self_evaluation')
        if self._context.get('collaborator_evaluation'):
            args = self._get_domain_collaborator(args)
        if self._context.get('leader_evaluation'):
            args = self._get_domain_leader_evaluation(args, )
        if self._context.get('environment_definition'):
            args = self._get_domain_evaluation(args, 'environment_definition')
        return args

    def _get_domain_leader_evaluation(self, args):
        collaborators = [x for x in args if x[0] == 'collaborators']
        if collaborators:
            args_extended = [('evaluation_type', '=', 'leader_evaluation'),
                             ('evaluator_id', '=', self.env.user.employee_id.id)]
        else:
            # BREAKPOINT - Todos los usuarios deben ver las evaluaciones en las que es evaluador
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
            operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
            args_extended = [
                ('evaluation_type', '=', 'leader_evaluation'),
                ('evaluator_id', '=', self.env.user.employee_id.id),
                ('inciso_id', '=', inciso_id),
                ('operating_unit_id', '=', operating_unit_id)
            ]
            # ESTRUCTURA INCISO-UE
            if self._is_group_admin_gh_inciso() or self._is_group_usuario_gh_inciso():
                args_extended = expression.OR(
                    [[('evaluated_id', '!=', self.env.user.employee_id.id), ('inciso_id', '=', inciso_id),
                      ('evaluation_type', '=', 'leader_evaluation')], args_extended])
            elif self._is_group_admin_gh_ue() or self._is_group_usuario_gh_ue():
                args_extended = expression.OR(
                    [[('evaluated_id', '!=', self.env.user.employee_id.id),
                      ('operating_unit_id', '=', operating_unit_id), ('evaluation_type', '=', 'leader_evaluation')],
                     args_extended])
            # REPONSABLE UO
            if self._is_group_responsable_uo():
                my_department = self.env.user.employee_id.job_id.department_id
                available_departments = my_department
                available_departments |= self.env['hr.department'].search([('id', 'child_of', my_department.id)])
                args_extended = expression.OR([[('evaluated_id', '!=', self.env.user.employee_id.id),
                                                ('uo_id', 'in', available_departments.ids),
                                                ('evaluation_type', '=', 'leader_evaluation')], args_extended])
        # SIEMPRE DEBO VER LAS EVALUACIONES EN LAS QUE SOY EVALUADOR ORIGINAL
        args_extended = expression.OR([[('original_evaluator_id', '=', self.env.user.employee_id.id),
                                        ('evaluation_type', '=', 'leader_evaluation')], args_extended])
        return expression.AND([args_extended, args])

    def _get_domain_evaluation(self, args, evaluation_type):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        args_extended = [
            ('evaluation_type', '=', evaluation_type),
            ('evaluated_id', '=', self.env.user.employee_id.id),
            ('inciso_id', '=', inciso_id),
            ('operating_unit_id', '=', operating_unit_id)
        ]
        if self._is_group_admin_gh_inciso():
            args_extended = expression.OR(
                [[('inciso_id', '=', inciso_id), ('evaluation_type', '=', evaluation_type)], args_extended])
        elif self._is_group_admin_gh_ue():
            args_extended = expression.OR(
                [[('operating_unit_id', '=', operating_unit_id), ('evaluation_type', '=', evaluation_type)],
                 args_extended])
        return expression.AND([args_extended, args])

    def _get_domain_collaborator(self, args):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id

        args_extended = [
            ('evaluator_id', '=', self.env.user.employee_id.id),
            ('inciso_id', '=', inciso_id),
            ('operating_unit_id', '=', operating_unit_id),
            ('evaluation_type', '=', 'collaborator')
        ]
        if self._is_group_admin_gh_inciso():
            args_extended = expression.OR([[('evaluated_id', '!=', self.env.user.employee_id.id), ('inciso_id', '=', inciso_id),
                                   ('evaluation_type', '=', 'collaborator')], args_extended])
        elif self._is_group_admin_gh_ue():
            args_extended = expression.OR([[('evaluated_id', '!=', self.env.user.employee_id.id),
                                    ('operating_unit_id', '=', operating_unit_id),
                                    ('evaluation_type', '=', 'collaborator')], args_extended])
        return expression.AND([args_extended, args])

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluation, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count,
                                                            access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    name = fields.Char(string="Nombre", compute="_compute_name", store=True)
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', required=True, readonly=True)
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado', readonly=True)
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador', readonly=True, tracking=True, index=True)
    evaluator_uo_id = fields.Many2one('hr.department', string='UO del Evaluador', readonly=True)
    original_evaluator_id = fields.Many2one('hr.employee', string='Evaluador Original', readonly=True)
    original_evaluator_uo_id = fields.Many2one('hr.department', string='UO del Evaluador Original', readonly=True)
    reason_change_id = fields.Many2one('onsc.desempeno.reason.change.evaluator', string='Motivo de cambio de Evaluador')

    # DEFINICION DE ENTORNO
    list_manager_id = fields.Many2one('hr.employee', string='Evaluador', readonly=True)
    environment_evaluation_ids = fields.Many2many('hr.employee', 'enviroment_evaluator_evaluation_rel', 'evaluation_id',
                                                  'enviroment_evaluator_id', string='Evaluación de Entorno',
                                                  readonly=True)
    environment_ids = fields.Many2many('hr.employee', string='Entorno')
    environment_ids_domain = fields.Char(compute='_compute_environment_ids_domain')
    environment_in_hierarchy = fields.Boolean(
        string='Definir entorno en la misma estructura jerárquica',
        default=True
    )
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='UE', readonly=True)
    uo_id = fields.Many2one('hr.department', string='UO', readonly=True)
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', readonly=True)
    level_id = fields.Many2one('onsc.desempeno.level', string='Nivel', readonly=True)
    evaluation_stage_id = fields.Many2one('onsc.desempeno.evaluation.stage', string='Evaluación 360', readonly=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', readonly=True)
    evaluation_list_id = fields.Many2one('onsc.desempeno.evaluation.list', string='Lista de participante', readonly=True)
    year = fields.Integer(string='Año a Evaluar', related='general_cycle_id.year')
    evaluation_start_date = fields.Date(
        string='Fecha inicio ciclo evaluación',
        related='evaluation_stage_id.start_date',
        store=True)
    evaluation_end_date = fields.Date(
        string='Fecha fin ciclo evaluación',
        related='evaluation_stage_id.end_date',
        store=True)
    environment_definition_end_date = fields.Date(
        string='Fecha de Fin de la Definición de Entorno',
        related='evaluation_stage_id.end_date_environment',
        store=True)
    evaluation_competency_ids = fields.One2many('onsc.desempeno.evaluation.competency', 'evaluation_id',
                                                string='Evaluación de Competencias')
    general_comments = fields.Text(string='Comentarios Generales')
    state = fields.Selection(STATE, string='Estado', default='draft', readonly=True, tracking=True)
    locked = fields.Boolean(string='Bloqueado')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    evaluation_form_edit = fields.Boolean('Puede editar el form?', compute='_compute_evaluation_form_edit')
    is_evaluation_form_active = fields.Boolean(
        compute=lambda s: s._get_is_evaluation_form_active('is_evaluation_form_active'),
        default=lambda s: s._get_is_evaluation_form_active('is_evaluation_form_active', True)
    )
    evaluation_form_text = fields.Text(
        compute=lambda s: s._get_evaluation_form_text('evaluation_form_text'),
        default=lambda s: s._get_evaluation_form_text('evaluation_form_text', True)
    )
    is_environment_evaluation_form_active = fields.Boolean(
        compute=lambda s: s._get_is_environment_evaluation_form_active('is_environment_evaluation_form_active'),
        default=lambda s: s._get_is_environment_evaluation_form_active('is_environment_evaluation_form_active', True)
    )
    environment_evaluation_text = fields.Text(
        compute=lambda s: s._get_environment_evaluation_text('environment_evaluation_text'),
        default=lambda s: s._get_environment_evaluation_text('environment_evaluation_text', True)
    )
    collaborators = fields.Boolean(string="Colaboradores directos", default=False)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)

    is_evaluation_change_available = fields.Boolean(
        string='Botón de cambio de evaluador disponible',
        compute='_compute_is_evaluation_change_available')

    def _get_evaluation_form_text(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    def _get_is_evaluation_form_active(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    def _get_environment_evaluation_text(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    def _get_is_environment_evaluation_form_active(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    def has_leader_evaluation(self):
        return self.env['onsc.desempeno.evaluation'].suspend_security().search_count(
            [('evaluator_id', '=', self.env.user.employee_id.id), ('evaluation_type', '=', 'collaborator')])

    @api.depends('evaluated_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            if record.evaluated_id and record.general_cycle_id:
                record.name = '%s - %s' % (record.evaluated_id.name, record.general_cycle_id.year)
            else:
                record.name = ''

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            # is_self_evaluation = record.evaluation_type == 'self_evaluation'
            second_condition = record.state not in ['in_process'] or record.evaluator_id.id != user_employee_id
            record.should_disable_form_edit = second_condition

    @api.depends('state')
    def _compute_evaluation_form_edit(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            # is_am_evaluated = record.evaluated_id.id == user_employee_id
            record.evaluation_form_edit = record.evaluator_id.id == user_employee_id

    @api.depends('state')
    def _compute_is_evaluation_change_available(self):
        is_gh_user = self._is_group_usuario_gh_inciso() or self._is_group_usuario_gh_ue()
        is_gh_responsable = self._is_group_responsable_uo()
        for record in self:
            is_user_gh_cond = is_gh_user and record.sudo().evaluator_uo_id.hierarchical_level_id.order == 1
            is_leader_eval = record.evaluation_type == 'leader_evaluation'
            record.is_evaluation_change_available = (is_user_gh_cond or is_gh_responsable) and is_leader_eval

    @api.depends('state', 'environment_in_hierarchy')
    def _compute_environment_ids_domain(self):
        user_employee = self.env.user.employee_id
        EvaluationList = self.env['onsc.desempeno.evaluation.list'].sudo()
        Job = self.env['hr.job'].sudo()
        for rec in self:
            if rec.evaluation_type == 'environment_definition':
                evaluation_lists = EvaluationList.search([
                    ('evaluation_stage_id.general_cycle_id', '=', rec.general_cycle_id.id)
                ])
                same_cycle_my_eval_lists = evaluation_lists.filtered(lambda x: x.manager_id.id == user_employee.id)
                same_cycle_collaborators = same_cycle_my_eval_lists.line_ids.mapped('employee_id')
                same_cycle_collaborators |= same_cycle_my_eval_lists.evaluation_generated_line_ids.mapped('employee_id')

                employees_2exclude = same_cycle_collaborators
                employees_2exclude |= user_employee
                employees_2exclude |= rec.list_manager_id

                domain = [
                    ('id', 'not in', employees_2exclude.ids)
                ]

                if rec.environment_in_hierarchy:
                    jobs = Job.get_active_jobs_in_hierarchy()
                    domain = expression.AND([domain, [('id', 'in', jobs.mapped('employee_id').ids)]])
            else:
                domain = [('id','in',[])]
            rec.environment_ids_domain = json.dumps(domain)

    def button_start_evaluation(self):
        self.write({'state': 'in_process'})

    def button_completed_evaluation(self):
        self._check_complete_evaluation()
        self.write({'state': 'completed'})

    def button_reopen_evaluation(self):
        self.write({'state': 'in_process'})

    def _check_complete_evaluation(self):
        if self.evaluation_type != 'environment_definition' and not self.general_comments:
            raise ValidationError(_("El campo comentarios generales es obligatorio"))

        for competency in self.evaluation_competency_ids:
            if not competency.degree_id or not competency.improvement_areas:
                raise ValidationError(
                    _('Deben estar todas las evaluaciones de competencias completas para poder pasar a "Completado"'))
