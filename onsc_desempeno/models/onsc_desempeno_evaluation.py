# -*- coding: utf-8 -*-
import json
import logging
import random

from dateutil.relativedelta import relativedelta

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
        if self._context.get('environment_evaluation'):
            args = self._get_domain_evaluation(args, 'environment_evaluation', show_evaluator=True)
        return args

    def _get_domain_leader_evaluation(self, args):
        collaborators = [x for x in args if x[0] == 'collaborators']
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        if collaborators:
            args_extended = [
                ('evaluation_type', '=', 'leader_evaluation'),
                ('evaluator_id', '=', self.env.user.employee_id.id),
                ('inciso_id', '=', inciso_id),
                ('operating_unit_id', '=', operating_unit_id)
            ]
        else:
            # BREAKPOINT - Todos los usuarios deben ver las evaluaciones en las que es evaluador
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

    def _get_domain_evaluation(self, args, evaluation_type, show_evaluator=False):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        args_extended = [
            ('evaluation_type', '=', evaluation_type),
            ('inciso_id', '=', inciso_id),
            ('operating_unit_id', '=', operating_unit_id)
        ]
        if show_evaluator:
            args_extended = expression.AND(
                [[('evaluator_id', '=', self.env.user.employee_id.id)], args_extended])
        else:
            args_extended = expression.AND(
                [[('evaluated_id', '=', self.env.user.employee_id.id)], args_extended])

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
            args_extended = expression.OR(
                [[('evaluated_id', '!=', self.env.user.employee_id.id), ('inciso_id', '=', inciso_id),
                  ('evaluation_type', '=', 'collaborator')], args_extended])
        elif self._is_group_admin_gh_ue():
            args_extended = expression.OR([[('evaluated_id', '!=', self.env.user.employee_id.id),
                                            ('operating_unit_id', '=', operating_unit_id),
                                            ('evaluation_type', '=', 'collaborator')], args_extended])
        return expression.AND([args_extended, args])

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluation, self)._search(args, offset=offset, limit=limit, order=order,
                                                            count=count,
                                                            access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and self._context.get('ignore_security_rules', False) is False:
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
    evaluation_list_id = fields.Many2one('onsc.desempeno.evaluation.list', string='Lista de participante',
                                         readonly=True)
    year = fields.Integer(string='Año a Evaluar', related='general_cycle_id.year', store=True)
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
        compute=lambda s: s._get_value_config('is_evaluation_form_active'),
        default=lambda s: s._get_value_config('is_evaluation_form_active', True)
    )
    evaluation_form_text = fields.Text(
        compute=lambda s: s._get_value_config('evaluation_form_text'),
        default=lambda s: s._get_value_config('evaluation_form_text', True)
    )
    is_environment_evaluation_form_active = fields.Boolean(
        compute=lambda s: s._get_value_config('is_environment_evaluation_form_active'),
        default=lambda s: s._get_value_config('is_environment_evaluation_form_active', True)
    )
    environment_evaluation_text = fields.Text(
        compute=lambda s: s._get_value_config('environment_evaluation_text'),
        default=lambda s: s._get_value_config('environment_evaluation_text', True)
    )
    collaborators = fields.Boolean(string="Colaboradores directos", default=False)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)

    is_evaluation_change_available = fields.Boolean(
        string='Botón de cambio de evaluador disponible',
        compute='_compute_is_evaluation_change_available')

    def _get_value_config(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    def has_leader_evaluation(self):
        return self.env['onsc.desempeno.evaluation'].suspend_security().search_count(
            [('evaluator_id', '=', self.env.user.employee_id.id), ('evaluation_type', '=', 'collaborator')])

    @api.constrains('environment_ids')
    def _check_environment_ids(self):
        max_environment_evaluation_forms = self.env.user.company_id.max_environment_evaluation_forms
        for rec in self:
            _len_environment_ids = len(rec.environment_ids)
            if _len_environment_ids < 2 or _len_environment_ids > 10:
                raise ValidationError(
                    _('La cantidad de evaluadores de entorno debe ser mayor a 2 y menor a 10!'))
            for environment_id in rec.environment_ids:
                if self.with_context(ignore_security_rules=True).search_count([
                    ('evaluation_type', 'in', ['environment_evaluation',
                                               'self_evaluation',
                                               'leader_evaluation',
                                               'collaborator'
                                               ]),
                    ('evaluator_id', '=', environment_id.id),
                    ('general_cycle_id', '=', rec.general_cycle_id.id),
                ]) > max_environment_evaluation_forms:
                    raise ValidationError(_('El funcionario %s no puede ser seleccionado como entorno, favor seleccionar otra persona') % (environment_id.full_name))

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
            condition = record.state not in ['in_process'] or record.evaluator_id.id != user_employee_id or record.locked
            record.should_disable_form_edit = condition

    @api.depends('state')
    def _compute_evaluation_form_edit(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            record.evaluation_form_edit = record.evaluator_id.id == user_employee_id and not record.locked

    @api.depends('state')
    def _compute_is_evaluation_change_available(self):
        Department = self.env['hr.department'].sudo()
        is_gh_user_ue = self._is_group_usuario_gh_ue()
        is_gh_user_inciso = self._is_group_usuario_gh_inciso()
        is_gh_responsable = self._is_group_responsable_uo()
        employee = self.env.user.employee_id
        for record in self:
            is_valid_evaluation = record.evaluation_type in ['leader_evaluation', 'gap_deal']
            is_am_evaluator = record.evaluator_id.id == employee.id
            is_order_1 = record.sudo().evaluator_uo_id.hierarchical_level_id.order == 1
            same_operating_unit = record.operating_unit_id.id == employee.job_id.contract_id.operating_unit_id.id
            same_inciso = record.inciso_id.id == employee.job_id.contract_id.inciso_id.id
            hierarchy_deparments = Department.search([('id', 'child_of', employee.job_id.department_id.id)])
            hierarchy_deparments |= employee.job_id.department_id

            is_user_gh_ue_cond = is_gh_user_ue and is_order_1 and same_operating_unit
            is_user_gh_inc_cond = is_gh_user_inciso and is_order_1 and same_inciso
            is_responsable = is_gh_responsable and record.uo_id.id in hierarchy_deparments.ids
            base_condition = (is_user_gh_ue_cond or is_user_gh_inc_cond or is_responsable)

            record.is_evaluation_change_available = base_condition and not is_am_evaluator and is_valid_evaluation

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
                domain = [('id', 'in', [])]
            rec.environment_ids_domain = json.dumps(domain)

    def button_start_evaluation(self):
        self.write({'state': 'in_process'})

    def button_completed_evaluation(self):
        self._check_complete_evaluation()
        self.write({'state': 'completed'})

    def button_environment_designated(self):
        self._check_environment_ids()
        self._generate_environment_evaluations()
        self.write({'state': 'completed'})

    def button_reopen_evaluation(self):
        self.write({'state': 'in_process'})

    def _generate_environment_evaluations(self):
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        for rec in self:
            random_environment_ids = []
            random_environments = random.sample(rec.environment_ids,
                                                self.env.user.company_id.random_environment_evaluation_forms)
            hierachy_manager_id = rec.uo_id.get_first_department_withmanager_in_tree().manager_id.id
            is_manager = hierachy_manager_id == rec.evaluated_id.id
            level_id = Level.suspend_security().search(
                [('hierarchical_level_id', '=', rec.uo_id.hierarchical_level_id.id),
                 ('is_uo_manager', '=', is_manager)]).mapped("level_id")
            if not level_id:
                raise ValidationError(
                    _(u"No existe nivel configurado para la combinación de nivel jerárquico y responsable UO"))
            skills = self.env['onsc.desempeno.skill.line'].suspend_security().search(
                [('level_id', '=', level_id.id)]).mapped('skill_id').filtered(lambda r: r.active)
            if not skills:
                raise ValidationError(_(u"No se ha encontrado ninguna competencia activa"))
            for random_environment in random_environments:
                random_environment_ids.append(random_environment.id)
                evaluation = self.suspend_security().create({
                    'evaluated_id': rec.evaluated_id.id,
                    'evaluator_id': random_environment.id,
                    # 'evaluator_uo_id': rec.evaluator_uo_id.id,
                    'evaluation_type': 'environment_evaluation',
                    'uo_id': rec.uo_id.id,
                    'inciso_id': rec.inciso_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                    'occupation_id': rec.occupation_id.id,
                    'level_id': level_id.id,
                    'evaluation_stage_id': rec.evaluation_stage_id.id,
                    'general_cycle_id': rec.general_cycle_id.id,
                    'state': 'draft',
                })
                for skill in skills:
                    Competency.create({'evaluation_id': evaluation.id,
                                       'skill_id': skill.id,
                                       'skill_line_ids': [(6, 0, skill.skill_line_ids.filtered(
                                           lambda r: r.level_id.id == evaluation.level_id.id).ids)]
                                       })
            rec.write({'environment_evaluation_ids': [(6, 0, random_environment_ids)]})

    def _check_complete_evaluation(self):
        if self.evaluation_type != 'environment_definition' and not self.general_comments:
            raise ValidationError(_("El campo comentarios generales es obligatorio"))

        for competency in self.evaluation_competency_ids:
            if not competency.degree_id or not competency.improvement_areas:
                raise ValidationError(
                    _('Deben estar todas las evaluaciones de competencias completas para poder pasar a "Completado"'))

    def notification_end_evaluation(self):
        year = fields.Date.today().strftime('%Y')
        days_notification_end_ev = self.env.user.company_id.days_notification_end_ev
        date_end = fields.Date.today() + relativedelta(days=days_notification_end_ev)
        count_message = self.search_count(
            [('evaluation_type', 'in', ['environment_evaluation', 'collaborator']), ('state', '!=', 'canceled'),
             ('year', '=', year), ('evaluation_end_date', '=', date_end)])
        if count_message > 0:
            generated_form_email_template_id = self.env.ref('onsc_desempeno.email_template_end_date_evaluation')
            generated_form_email_template_id.send_mail(self.id, force_send=True)

        count_message_env = self.search_count(
            [('evaluation_type', 'in', ['environment_definition']), ('state', '!=', 'canceled'),
             ('year', '=', year),
             ('environment_definition_end_date', '=', date_end)])

        if count_message_env > 0:
            generated_form_email_template_id = self.env.ref('onsc_desempeno.email_template_end_date_environment_definition')
            generated_form_email_template_id.send_mail(self.id, force_send=True)

    def get_followers_mails(self):
        year = fields.Date.today().strftime('%Y')
        message_partner_ids = self.search(
            [('evaluation_type', 'in', ['environment_evaluation', 'collaborator']), ('state', '!=', 'canceled'),
             ('year', '=', year)]).mapped('evaluator_id.partner_id')
        return message_partner_ids.get_onsc_mails()

    def get_environment_definition_followers_mails(self):
        year = fields.Date.today().strftime('%Y')
        message_partner_ids = self.search(
            [('evaluation_type', '=', 'environment_definition'), ('state', '!=', 'canceled'),
             ('year', '=', year)]).mapped('evaluated_id.partner_id')
        return message_partner_ids.get_onsc_mails()

    def process_end_block_evaluation(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        general_ids = GeneralCycle.search([('end_date_max', '=', fields.Date.today())]).ids

        for record in self.search(
                [('general_cycle_id', 'in', general_ids), ('state', 'not in', ['canceled', 'finished', 'uncompleted']),
                 ('evaluation_type', 'in', ['self_evaluation', 'leader_evaluation'])]):
            if record.state == 'completed':
                record.write({'state': 'finished'})
            else:
                record.write({'state': 'uncompleted'})

        for record in self.search(
                [('environment_definition_end_date', '=', fields.Date.today()),
                 ('state', 'not in', ['canceled', 'finished', 'uncompleted']),
                 ('evaluation_type', 'in', ['environment_definition'])]):
            if record.state == 'completed':
                record.write({'state': 'finished'})
            else:
                record.write({'state': 'uncompleted'})

        self.search([('evaluation_end_date', '=', fields.Date.today()), ('state', '!=', 'canceled'),
                     ('evaluation_type', 'in', ['environment_evaluation', 'collaborator'])]).write(
            {'locked': True})
