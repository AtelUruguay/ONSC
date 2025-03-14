# -*- coding: utf-8 -*-
import json
import logging
import random
from lxml import etree

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

_EVALUATION_360 = {
    'self_evaluation',
    'collaborator',
    'leader_evaluation',
    'environment_evaluation'
}  # Evaluaciones 360


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

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCDesempenoEvaluation, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                   toolbar=toolbar,
                                                                   submenu=submenu)
        doc = etree.XML(res['arch'])
        views_editables = self._context.get('environment_definition') or self._context.get('development_plan')
        if view_type in ['form', ] and self._context.get('is_from_menu') and views_editables:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('edit', '1')
        elif 'edit' in self._context and not self._context.get('edit'):
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('edit', '0')

        if view_type in ['form', ] and self._context.get('is_from_menu') and self._context.get('tracing_plan'):
            for node_form in doc.xpath("//button[@name='button_agree_plan_leader']"):
                node_form.set(
                    'confirm', '¿Está seguro que desea confirmar? Recuerde que solamente debe finalizar una vez que se haya cargado la actualización del último avance alcanzado')
                node_form.set('string', 'Acordar Líder')
            for node_form in doc.xpath("//button[@name='button_agree_plan_evaluated']"):
                node_form.set(
                    'confirm', '¿Está seguro que desea confirmar? Recuerde que solamente debe finalizar una vez que se haya cargado la actualización del último avance alcanzado')
                node_form.set('string', 'Acordar Evaluado')
        if view_type in ['form', ] and self._context.get('is_from_menu') and self._context.get('develop_plan'):
            for node_form in doc.xpath("//button[@name='button_agree_gh']"):
                node_form.set('confirm', '¿Está seguro que desea confirmar?')
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCDesempenoEvaluation, self).fields_get(allfields, attributes)
        hide = ['__last_update', 'activity_date_deadline', 'activity_exception_decoration',
                'activity_exception_icon', 'activity_ids', 'activity_state', 'activity_summary',
                'activity_type_icon', 'activity_type_id', 'activity_user_id ', 'create_date', 'create_uid',
                'display_name', 'full_environment_ids_domain', 'environment_evaluation_text',
                'has_message', 'is_agree_button_gh_available', 'is_agree_evaluation_evaluated_available',
                'is_agree_evaluation_leader_available', 'is_cancel_available', 'is_development_plan_not_generated',
                'is_edit_general_comments', 'is_environment_evaluation_form_active', 'is_evaluation_change_available',
                'is_gap_deal_not_generated', 'message_attachment_count',
                'message_has_error',
                'message_has_error_counter', 'message_has_sms_error', 'message_ids', 'message_is_follower',
                'message_main_attachment_id', 'message_needaction', 'message_needaction_counter', 'message_partner_ids',
                'message_unread', 'message_unread_counter', 'my_activity_date_deadline',
                'should_disable_form_edit', 'show_button_cancel', 'show_button_go_back',
                'state_before_cancel', 'website_message_ids', 'write_date', 'write_uid', 'general_cycle_id',
                'list_manager_id', 'use_original_evaluator', 'environment_in_hierarchy', 'evaluation_competency_ids',
                'gap_deal_competency_ids', 'tracing_plan_ids', 'development_plan_ids']

        hide_env = ['environment_definition_end_date', 'environment_in_hierarchy', 'evaluator_id']

        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False

        if self._context.get('gap_deal') or self._context.get('develop_plan', False):
            res['state']['selectable'] = False
            res['state']['searchable'] = False
            res['state']['sortable'] = False

        else:
            res['state_gap_deal']['selectable'] = False
            res['state_gap_deal']['searchable'] = False
            res['state_gap_deal']['sortable'] = False
            res['gap_deal_state']['selectable'] = False
            res['gap_deal_state']['searchable'] = False
            res['gap_deal_state']['sortable'] = False

        if self._context.get('gap_deal'):
            res['evaluation_end_date']['selectable'] = False
            res['evaluation_end_date']['searchable'] = False
            res['evaluation_end_date']['sortable'] = False

        else:
            res['evaluation_end_date_max']['selectable'] = False
            res['evaluation_end_date_max']['searchable'] = False
            res['evaluation_end_date_max']['sortable'] = False

        if self._context.get('environment_definition'):
            for field in hide_env:
                if field in res:
                    res[field]['selectable'] = False
                    res[field]['searchable'] = False
                    res[field]['sortable'] = False

        return res

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
        if self._context.get('gap_deal_type') or self._context.get('develop_plan') or self._context.get(
                'tracing_plan_type'):
            args = self._get_domain_gap_deal(args)

        return args

    def _get_domain_leader_evaluation(self, args):
        collaborators = [x for x in args if x[0] == 'collaborators']
        evaluations = [x for x in args if x[0] == 'evaluations']
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        if collaborators or evaluations:
            args_extended = [
                ('evaluation_type', '=', 'leader_evaluation'),
                ('evaluator_id', '=', self.env.user.employee_id.id),
                ('inciso_id', '=', inciso_id)]
            if not self._is_group_admin_gh_inciso() and not self._is_group_usuario_gh_inciso():
                args_extended = expression.AND(
                    [[('operating_unit_id', '=', operating_unit_id)], args_extended])
            if self._is_group_admin_gh_inciso() or self._is_group_admin_gh_ue():
                args_extended = expression.AND(
                    [[('evaluated_id', '!=', self.env.user.employee_id.id)], args_extended])
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
        evaluations = [x for x in args if x[0] == 'evaluations']
        args_extended = [
            ('evaluation_type', '=', evaluation_type),
            ('inciso_id', '=', inciso_id),
            ('operating_unit_id', '=', operating_unit_id)
        ]
        if evaluations:
            args_extended = expression.AND(
                [[('evaluator_id', '=', self.env.user.employee_id.id)], args_extended])
        else:
            if show_evaluator:
                args_extended = expression.AND(
                    [[('evaluator_id', '=', self.env.user.employee_id.id)], args_extended])
            else:
                args_extended = expression.AND(
                    [[('evaluated_id', '=', self.env.user.employee_id.id)], args_extended])

            if self._is_group_admin_gh_inciso():
                if evaluation_type == 'environment_evaluation':
                    args_extended = expression.OR([[
                        ('evaluated_id', '!=', self.env.user.employee_id.id),
                        ('inciso_id', '=', inciso_id),
                        ('evaluation_type', '=', evaluation_type)
                    ], args_extended])
                else:
                    args_extended = expression.OR([[
                        ('inciso_id', '=', inciso_id),
                        ('evaluation_type', '=', evaluation_type)
                    ], args_extended])
            elif self._is_group_admin_gh_ue():
                if evaluation_type == 'environment_evaluation':
                    args_extended = expression.OR([[
                        ('evaluated_id', '!=', self.env.user.employee_id.id),
                        ('operating_unit_id', '=', operating_unit_id),
                        ('evaluation_type', '=', evaluation_type)
                    ], args_extended])
                else:
                    args_extended = expression.OR([[
                        ('operating_unit_id', '=', operating_unit_id),
                        ('evaluation_type', '=', evaluation_type)
                    ], args_extended])
        if evaluation_type == 'environment_evaluation':
            args_extended = expression.OR([[
                ('evaluator_id', '=', self.env.user.employee_id.id),
                ('evaluation_type', '=', evaluation_type)
            ], args_extended])
        return expression.AND([args_extended, args])

    def _get_domain_gap_deal(self, args):
        if self._context.get('gap_deal_type'):
            evaluation_type = 'gap_deal'
        elif self._context.get('develop_plan'):
            evaluation_type = 'development_plan'
        elif self._context.get('tracing_plan_type'):
            evaluation_type = 'tracing_plan'
        collaborators = [x for x in args if x[0] == 'collaborators']
        evaluations = [x for x in args if x[0] == 'evaluations']
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        if evaluations:
            args_extended = [
                ('evaluation_type', '=', evaluation_type),
                ('evaluated_id', '=', self.env.user.employee_id.id),
                ('inciso_id', '=', inciso_id)
            ]
            if not self._is_group_admin_gh_inciso() and not self._is_group_usuario_gh_inciso():
                args_extended = expression.AND(
                    [[('operating_unit_id', '=', operating_unit_id)], args_extended])
        else:
            if collaborators:
                args_extended = [
                    ('evaluation_type', '=', evaluation_type),
                    ('evaluator_id', '=', self.env.user.employee_id.id),
                    ('inciso_id', '=', inciso_id)
                ]
                if not self._is_group_admin_gh_inciso() and not self._is_group_usuario_gh_inciso():
                    args_extended = expression.AND(
                        [[('operating_unit_id', '=', operating_unit_id)], args_extended])
            else:
                args_extended = [
                    ('evaluation_type', '=', evaluation_type),
                    ('inciso_id', '=', inciso_id),
                    ('operating_unit_id', '=', operating_unit_id),
                    '|', ('evaluator_id', '=', self.env.user.employee_id.id),
                    ('evaluated_id', '=', self.env.user.employee_id.id)
                ]
                if self._is_group_admin_gh_inciso() or self._is_group_usuario_gh_inciso():
                    args_extended = expression.OR(
                        [[('inciso_id', '=', inciso_id), ('evaluation_type', '=', evaluation_type)], args_extended])
                elif self._is_group_admin_gh_ue() or self._is_group_usuario_gh_ue():
                    args_extended = expression.OR(
                        [[('operating_unit_id', '=', operating_unit_id), ('evaluation_type', '=', evaluation_type)],
                         args_extended])
                # REPONSABLE UO
                if self._is_group_responsable_uo():
                    my_department = self.env.user.employee_id.job_id.department_id
                    available_departments = my_department
                    available_departments |= self.env['hr.department'].search([('id', 'child_of', my_department.id)])
                    args_extended = expression.OR([[
                        ('uo_id', 'in', available_departments.ids),
                        ('evaluation_type', '=', evaluation_type)], args_extended])
            args_extended = expression.OR([[('original_evaluator_id', '=', self.env.user.employee_id.id),
                                            ('evaluation_type', '=', evaluation_type)], args_extended])

        return expression.AND([args_extended, args])

    def _get_domain_collaborator(self, args):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        evaluations = [x for x in args if x[0] == 'evaluations']
        args_extended = [
            ('evaluator_id', '=', self.env.user.employee_id.id),
            ('inciso_id', '=', inciso_id),
            ('operating_unit_id', '=', operating_unit_id),
            ('evaluation_type', '=', 'collaborator')
        ]
        if not evaluations:
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
            _logger.info('*********** EVALUATION SEARCH DOMAIN IN ******************')
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

    evaluator_current_job_id = fields.Many2one(
        'hr.job',
        copy=False,
        string='Puesto actual del evaluador',
        help=u'Usado para en caso de cambio de puesto saber el Puesto actual '
             'en el que se encuentra el Funcionario que es Evaluador')
    current_job_id = fields.Many2one(
        'hr.job',
        copy=False,
        string='Puesto actual',
        help=u'Usado para en caso de cambio de puesto saber el Puesto actual '
             'en el que se encuentra el Funcionario')

    # DEFINICION DE ENTORNO
    list_manager_id = fields.Many2one('hr.employee', string='Evaluador', readonly=True)
    environment_evaluation_ids = fields.Many2many('hr.employee', 'enviroment_evaluator_evaluation_rel', 'evaluation_id',
                                                  'enviroment_evaluator_id', string='Evaluación de Entorno',
                                                  readonly=True)
    # environment_ids = fields.Many2many('hr.employee', string='Entorno')
    full_environment_ids = fields.Many2many('hr.job', string='Entorno')
    # environment_ids_domain = fields.Char(compute='_compute_environment_ids_domain')
    full_environment_ids_domain = fields.Char(compute='_compute_environment_ids_domain')
    environment_in_hierarchy = fields.Boolean(
        string='Definir entorno en la misma estructura jerárquica',
        default=True
    )

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='UE', readonly=True)
    uo_id = fields.Many2one('hr.department', string='UO', readonly=True)
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
        string='Fecha fin ciclo evaluación (Ciclo 360)',
        related='evaluation_stage_id.end_date',
        store=True)
    environment_definition_end_date = fields.Date(
        string='Fecha de Fin de la Definición de Entorno',
        related='evaluation_stage_id.end_date_environment',
        store=True)
    evaluation_end_date_max = fields.Date(
        string='Fecha fin ciclo evaluación (Ciclo General)',
        related='general_cycle_id.end_date_max',
        store=True)
    evaluation_competency_ids = fields.One2many('onsc.desempeno.evaluation.competency', 'evaluation_id',
                                                string='Evaluación de Competencias')
    gap_deal_competency_ids = fields.One2many('onsc.desempeno.evaluation.competency', 'gap_deal_id',
                                              string='Evaluación de Competencias')
    general_comments = fields.Text(string='Comentarios Generales')
    state = fields.Selection(STATE, string='Estado', default='draft', readonly=True, tracking=True)
    state_gap_deal = fields.Selection(STATE, string="Estado", default='draft', readonly=True, tracking=True)
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
    is_agree_evaluation_evaluated_available = fields.Boolean(
        string='Botón de Acordar Evaluación Evaluado',
        compute='_compute_is_agree_evaluation_evaluated_available')
    is_agree_evaluation_leader_available = fields.Boolean(
        string='Botón de Acordar Evaluación Líder',
        compute='_compute_is_agree_evaluation_leader_available')
    is_agree_button_gh_available = fields.Boolean(
        string='Botón de Acordar Evaluación Líder',
        compute='_compute_is_agree_button_gh_available')
    gap_deal_state = fields.Selection(
        selection=GAP_DEAL_STATES,
        string="Subestado",
        default='no_deal', tracking=True
    )
    is_gap_deal_not_generated = fields.Boolean(string='Acuerdo de brecha no generado', copy=False)
    is_edit_general_comments = fields.Boolean(
        string='Editable los comentarios generales',
        compute='_compute_is_edit_general_comments')

    development_plan_ids = fields.One2many('onsc.desempeno.evaluation.development.competency', 'evaluation_id',
                                           string='Competencia a desarrollar')
    is_development_plan_not_generated = fields.Boolean(string='Plan de desarrollo no generado')
    tracing_plan_ids = fields.One2many('onsc.desempeno.evaluation.development.competency', 'tracing_id',
                                       string='Competencia a desarrollar')
    use_original_evaluator = fields.Boolean(string='Crear seguimiento con evaluador original', default=False)

    is_cancel_available = fields.Boolean(
        string='Botón de cancelar disponible',
        compute='_compute_is_cancel_available')
    is_canceled_by_employee_out = fields.Boolean(
        string='¿Es cancelación por baja de funcionario?',
        copy=False,
        required=False)
    state_before_cancel = fields.Selection(STATE, string="Estado")
    reason_cancel = fields.Text(string='Motivo de cancelación')
    show_button_go_back = fields.Boolean('Ver botón volver atras', compute='_compute_show_button_go_back')
    show_button_cancel = fields.Boolean('Ver botón cancelar atras', compute='_compute_show_button_cancel')
    evaluations = fields.Boolean(string="Mis evaluaciones", default=False)
    is_pilot = fields.Boolean(string='¿Es piloto?', copy=False, related="general_cycle_id.is_pilot", store=True)
    is_button_reopen_evaluation_available = fields.Boolean(
        string='¿Está el botón de Reabrir seguimiento visible?',
        compute='_compute_is_button_reopen_evaluation_available')
    is_notebook_available = fields.Boolean(
        '¿Está disponible el Notebook?',
        compute='_compute_is_notebook_available')

    def _get_value_config(self, help_field='', is_default=False):
        _url = eval('self.env.user.company_id.%s' % help_field)
        if is_default:
            return _url
        for rec in self:
            setattr(rec, help_field, _url)

    def has_leader_evaluation(self):
        return self.env['onsc.desempeno.evaluation'].suspend_security().search_count(
            [('evaluator_id', '=', self.env.user.employee_id.id), ('evaluation_type', '=', 'collaborator')])

    @api.constrains('full_environment_ids')
    def _check_environment_ids(self):
        max_environment_evaluation_forms = self.env.user.company_id.max_environment_evaluation_forms
        max_environment_evaluation_leader_forms = self.env.user.company_id.max_environment_evaluation_leader_forms
        for rec in self:
            _len_environment_ids = len(rec.full_environment_ids)
            if not self.env.context.get("gap_deal") and _len_environment_ids < 2:
                raise ValidationError(_('No se puede designar el entorno, debe definir un mínimo de 2 personas, '
                                        'de lo contrario avanzará a la siguiente etapa sin el consolidado de entorno!'))
            if not self.env.context.get("gap_deal") and _len_environment_ids > 10:
                raise ValidationError(_('La cantidad de evaluadores de entorno debe ser menor a 10!'))
            environment_employee = {}
            for environment_id in rec.full_environment_ids:
                environment_employee[environment_id.employee_id.id] = environment_employee.get(
                    environment_id.employee_id.id, 0) + 1
                if environment_employee[environment_id.employee_id.id] > 1:
                    raise ValidationError(_('El funcionario %s no puede ser seleccionado en más de una ocasión, '
                                            'favor seleccionar otra persona') % (environment_id.employee_id.full_name))
                # SE CONSIDERA +1 PORQUE LA NUEVA YA EXCEDERIA EL TOPE MAXIMO PERMITIDO Y ESTE CONTROL ES PREVIO A LA GENERACION DE LA NUEVA DEF ENTORNO
                leader_evaluations_qty = self.with_context(ignore_security_rules=True).search_count([
                    ('evaluation_type', '=', 'leader_evaluation'),
                    ('evaluator_id', '=', environment_id.employee_id.id),
                    ('general_cycle_id', '=', rec.general_cycle_id.id),
                ])
                if leader_evaluations_qty >= max_environment_evaluation_forms:
                    evaluation_type_args = [
                        'environment_evaluation',
                        'self_evaluation',
                        'collaborator'
                    ]
                    value_restrict_to_use = max_environment_evaluation_leader_forms
                else:
                    evaluation_type_args = [
                        'environment_evaluation',
                        'self_evaluation',
                        'leader_evaluation',
                        'collaborator'
                    ]
                    value_restrict_to_use = max_environment_evaluation_forms
                if self.with_context(ignore_security_rules=True).search_count([
                    ('evaluation_type', 'in', evaluation_type_args),
                    ('evaluator_id', '=', environment_id.employee_id.id),
                    ('general_cycle_id', '=', rec.general_cycle_id.id),
                ]) + 1 > value_restrict_to_use:
                    raise ValidationError(
                        _('El funcionario %s no puede ser seleccionado como entorno, favor seleccionar otra persona') % (
                            environment_id.employee_id.full_name))

    @api.depends('evaluated_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            if record.evaluated_id and record.general_cycle_id:
                record.name = '%s - %s' % (record.evaluated_id.name, record.general_cycle_id.year)
            else:
                record.name = ''

    @api.depends('state', 'gap_deal_state')
    def _compute_should_disable_form_edit(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            if self._context.get('readonly_evaluation'):
                condition = True
            elif record.evaluation_type in ('gap_deal', 'development_plan'):
                _base_cond1 = record.is_agree_button_gh_available and record.evaluator_id.id != user_employee_id
                _cond1 = record.state_gap_deal != 'in_process' or record.gap_deal_state != 'no_deal' or _base_cond1
                _cond2 = record.evaluator_id.id != user_employee_id and record.evaluated_id.id != user_employee_id
                condition = _cond1 or _cond2
            elif record.evaluation_type == 'tracing_plan':
                _cond1 = record.is_agree_button_gh_available and record.evaluator_id.id != user_employee_id
                condition = record.state != 'in_process' or record.evaluator_id.id != user_employee_id or _cond1
            else:
                _cond1 = record.evaluator_id.id != user_employee_id or record.locked
                condition = record.state not in ['in_process'] or _cond1
            record.should_disable_form_edit = condition

    @api.depends('state','gap_deal_state', 'state_gap_deal')
    def _compute_is_agree_evaluation_leader_available(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            is_am_evaluator = record.evaluator_id.id == user_employee_id
            _is_valid_1 = record.evaluation_type in ('gap_deal', 'development_plan') and record.state_gap_deal == 'in_process'
            _is_valid_2 = record.evaluation_type == 'tracing_plan' and record.state == 'in_process'
            is_valid = (_is_valid_1 or _is_valid_2) and record.gap_deal_state != 'agree_leader'
            record.is_agree_evaluation_leader_available = is_am_evaluator and is_valid

    @api.depends('state', 'state_gap_deal')
    def _compute_is_agree_button_gh_available(self):
        Department = self.env['hr.department'].sudo()
        employee = self.env.user.employee_id
        user_employee_id = self.env.user.employee_id.id
        is_gh_responsable = self._is_group_responsable_uo()
        is_gh_user_ue = self._is_group_usuario_gh_ue()
        is_gh_user_inciso = self._is_group_usuario_gh_inciso()
        hierarchy_deparments = Department.search([('id', 'child_of', employee.job_id.department_id.id)])
        hierarchy_deparments |= employee.job_id.department_id
        for rec in self:
            is_am_evaluator = rec.evaluator_id.id == user_employee_id
            valid_state = (rec.state_gap_deal in ['in_process'] or rec.state in ['in_process'])
            valid_state1 = rec.evaluation_type in ['gap_deal', 'development_plan'] and rec.gap_deal_state in ['no_deal']
            valid_state_no_deal = valid_state1 or rec.evaluation_type == 'tracing_plan'
            valid_types = rec.evaluation_type in ['gap_deal', 'development_plan', 'tracing_plan']
            is_valid = valid_types and valid_state and valid_state_no_deal
            is_responsable = is_gh_responsable and rec.uo_id.id in hierarchy_deparments.ids
            user_security = not is_responsable and (is_gh_user_ue or is_gh_user_inciso)
            rec.is_agree_button_gh_available = is_am_evaluator and is_valid and user_security

    @api.depends('state', 'gap_deal_state', 'state_gap_deal')
    def _compute_is_agree_evaluation_evaluated_available(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            is_am_evaluated = record.evaluated_id.id == user_employee_id
            is_valid_1 = record.evaluation_type in ('gap_deal', 'development_plan') and not record.gap_deal_state == 'agree_evaluated' and record.state_gap_deal == 'in_process'
            is_valid_2 = record.evaluation_type == 'tracing_plan' and not record.gap_deal_state == 'agree_evaluated' and record.state == 'in_process'
            record.is_agree_evaluation_evaluated_available = is_am_evaluated and (is_valid_1 or is_valid_2)

    @api.depends('state', 'evaluator_id', 'evaluated_id')
    def _compute_evaluation_form_edit(self):
        user_employee_id = self.env.user.employee_id
        for record in self:
            if record.evaluation_type in ('development_plan', 'gap_deal'):
                record.evaluation_form_edit = record.evaluator_id.id == user_employee_id.id or record.evaluated_id.id == user_employee_id.id
            elif record.evaluation_type == 'tracing_plan':
                record.evaluation_form_edit = record.evaluator_id.id == user_employee_id.id
            else:
                record.evaluation_form_edit = record.evaluator_id.id == user_employee_id.id and not record.locked

    @api.depends('state')
    def _compute_is_evaluation_change_available(self):
        Department = self.env['hr.department'].sudo()
        is_gh_user_ue = self._is_group_usuario_gh_ue()
        is_gh_user_inciso = self._is_group_usuario_gh_inciso()
        is_gh_responsable = self._is_group_responsable_uo()
        employee = self.env.user.employee_id
        hierarchy_deparments = Department.search([('id', 'child_of', employee.job_id.department_id.id)])
        hierarchy_deparments |= employee.job_id.department_id
        for record in self:
            if record.evaluated_id.id == employee.id:
                record.is_evaluation_change_available = False
            else:
                same_operating_unit = record.operating_unit_id.id == employee.job_id.contract_id.operating_unit_id.id
                same_inciso = record.inciso_id.id == employee.job_id.contract_id.inciso_id.id
                is_am_orig_evaluator = record.original_evaluator_id.id == employee.id
                is_user_gh_ue_cond = is_gh_user_ue and same_operating_unit
                is_user_gh_inc_cond = is_gh_user_inciso and same_inciso
                is_am_evaluator = record.evaluator_id.id == employee.id
                is_responsable = is_gh_responsable and record.uo_id.id in hierarchy_deparments.ids
                is_order_1 = record.sudo().evaluator_uo_id.hierarchical_level_id.order == 1
                is_gap_deal = record.sudo().evaluation_type == 'gap_deal'
                _valid_state_gap_deal = record.state_gap_deal in ['draft', 'in_process']
                _valid_states = record.state in ['draft', 'in_process']
                _is_leader_eval = record.evaluation_type == 'leader_evaluation'
                _is_valid_leader_eval_1 = is_order_1 or is_responsable or is_am_orig_evaluator

                is_valid_gap_deal = record.evaluation_type == 'gap_deal' and _valid_state_gap_deal
                is_valid_development_plan = record.evaluation_type == 'development_plan' and _valid_state_gap_deal
                is_valid_leader_eval = _is_leader_eval and _valid_states and _is_valid_leader_eval_1
                is_valid_tracing_plan = record.evaluation_type == 'tracing_plan' and _valid_states
                is_valid_evaluation_1 = is_valid_gap_deal or is_valid_leader_eval
                is_valid_evaluation_2 = is_valid_development_plan or is_valid_tracing_plan
                is_valid_evaluation = is_valid_evaluation_1 or is_valid_evaluation_2

                _is_gap_deal_evaluator1 = is_user_gh_inc_cond or is_user_gh_ue_cond or is_am_orig_evaluator
                is_gap_deal_evaluator = is_gap_deal and _is_gap_deal_evaluator1

                base_condition = is_user_gh_ue_cond or is_user_gh_inc_cond or is_responsable or is_gap_deal_evaluator
                record.is_evaluation_change_available = base_condition and not is_am_evaluator and is_valid_evaluation

    @api.depends('state')
    def _compute_is_cancel_available(self):
        Score = self.env['onsc.desempeno.score'].suspend_security()
        is_gh_user_ue = self._is_group_usuario_gh_ue()
        is_gh_user_inciso = self._is_group_usuario_gh_inciso()
        for record in self:
            notified_qty = Score.search_count([('evaluation_stage_id', '=', record.evaluation_stage_id.id),
                                               ('employee_id', '=', record.evaluator_id.id),
                                               ('is_employee_notified', '=', True)])
            record.is_cancel_available = (is_gh_user_ue or is_gh_user_inciso) and notified_qty == 0

    def _compute_is_notebook_available(self):
        user_employee = self.env.user.employee_id
        user_restricted = self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue,onsc_desempeno.group_desempeno_admin_gh_inciso,onsc_desempeno.group_desempeno_usuario_gh_inciso,onsc_desempeno.group_desempeno_usuario_gh_ue')
        for record in self:
            if not user_restricted:
                record.is_notebook_available = True
            else:
                is_iam_evaluated = record.evaluated_id.id == user_employee.id
                is_iam_evaluator = record.evaluator_id.id == user_employee.id
                is_am_orig_evaluator = record.original_evaluator_id.id == user_employee.id
                if self._is_group_responsable_uo():
                    my_department = user_employee.job_id.department_id
                    available_departments = my_department
                    available_departments |= self.env['hr.department'].search([('id', 'child_of', my_department.id)])
                    is_am_responsable = record.uo_id.id in available_departments.ids
                else:
                    is_am_responsable = False

                is_eval_valid_cond1 = is_iam_evaluator or is_am_orig_evaluator
                is_eval_valid_cond2 = is_eval_valid_cond1 or is_am_responsable

                cond1 = record.evaluation_type in ['collaborator', 'environment_evaluation'] and is_eval_valid_cond1
                cond2 = record.evaluation_type == 'leader_evaluation' and is_eval_valid_cond2
                cond3 = record.evaluation_type == 'self_evaluation' and is_iam_evaluated

                record.is_notebook_available = cond1 or cond2 or cond3 or record.evaluation_type == 'gap_deal'

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

                today = str(fields.Date.today())
                domain = [
                    ('employee_id', 'not in', employees_2exclude.ids),
                    '&', ('start_date', '<=', today),
                    '|', ('end_date', '>=', today), ('end_date', '=', False)
                ]
                if rec.environment_in_hierarchy:
                    jobs = Job.get_active_jobs_in_hierarchy()
                    # domain = expression.AND([domain, [('id', 'in', jobs.mapped('employee_id').ids)]])
                    domain = expression.AND([domain, [('id', 'in', jobs.ids)]])
            else:
                # domain = [('id', 'in', [])]
                domain = [('id', 'in', [])]
            # rec.environment_ids_domain = json.dumps(domain)
            rec.full_environment_ids_domain = json.dumps(domain)

    @api.depends('state', 'gap_deal_state')
    def _compute_is_edit_general_comments(self):
        user_employee_id = self.env.user.employee_id.id
        for record in self:
            if record.evaluation_type == 'gap_deal':
                _states = record.state_gap_deal not in ['canceled', 'in_process']
                _cond1 = _states or record.gap_deal_state != 'no_deal'
                _cond2 = record.evaluator_id.id != user_employee_id and record.evaluated_id.id != user_employee_id
                condition = _cond1 or _cond2
            else:
                _states = record.state not in ['canceled', 'in_process']
                condition = _states or record.evaluator_id.id != user_employee_id or record.locked
            record.is_edit_general_comments = condition

    @api.depends('state')
    def _compute_is_button_reopen_evaluation_available(self):
        _today = fields.Date.today()
        for record in self:
            record.is_button_reopen_evaluation_available = record.general_cycle_id.end_date > _today

    @api.depends('state', 'gap_deal_state')
    def _compute_show_button_go_back(self):
        for record in self:
            if record.evaluation_type in ('gap_deal', 'development_plan'):
                condition = record.state_gap_deal == 'canceled' and not record.is_canceled_by_employee_out
            else:
                condition = record.state == 'canceled' and not record.is_canceled_by_employee_out
            record.show_button_go_back = condition

    @api.depends('state', 'gap_deal_state')
    def _compute_show_button_cancel(self):
        for record in self:
            if record.evaluation_type in ('gap_deal'):
                condition = record.state_gap_deal != 'canceled'
            elif record.evaluation_type in ('development_plan'):
                condition = record.state_gap_deal != 'canceled'
            else:
                condition = record.state != 'canceled'
            record.show_button_cancel = condition

    def button_start_evaluation(self):
        if self.evaluation_type in ('gap_deal', 'development_plan'):
            self.write({'state_gap_deal': 'in_process'})
        else:
            self.write({'state': 'in_process'})

    def button_finish_evaluation(self):
        self._check_at_least_one_tracing()
        self.write({'state': 'finished'})

    def _check_at_least_one_tracing(self):
        Tracing = self.env['onsc.desempeno.evaluation.tracing.plan'].sudo()
        if Tracing.search_count([('develop_means_id', 'in', self.tracing_plan_ids.development_means_ids.ids)]) == 0:
            raise ValidationError(
                _('Debe existir al menos un seguimiento ingresado para poder finalizar'))


    def button_completed_evaluation(self):
        self._check_complete_evaluation()
        self.write({'state': 'completed'})

    def button_environment_designated(self):
        self._check_environment_ids()
        self._generate_environment_evaluations()
        self.write({'state': 'completed'})

    def button_reopen_tracing_deal(self):
        self.button_reopen_evaluation()

    def button_reopen_evaluation(self):
        if self.evaluation_type not in _EVALUATION_360 and self.filtered(lambda x: x.state != 'finished'):
            raise ValidationError(_("Esta evaluación ha sido modificada. Por favor, vuelva al menú y acceda nuevamente a la misma"))
        self.write({'gap_deal_state': 'no_deal', 'state': 'in_process'})

    def button_reopen_deal(self):
        if self.filtered(lambda x: x.state_gap_deal != 'in_process'):
            raise ValidationError(_("Esta evaluación ha sido modificada. Por favor, vuelva al menú y acceda nuevamente a la misma"))
        self.write({'gap_deal_state': 'no_deal', 'state_gap_deal': 'in_process'})

    def button_agree_evaluation_leader(self):
        self._check_complete_evaluation()
        if self.gap_deal_state == 'no_deal':
            self.write({'gap_deal_state': 'agree_leader'})
        elif self.gap_deal_state == 'agree_evaluated':
            self.suspend_security()._create_development_plan()
            self.write({'state_gap_deal': 'deal_close', 'gap_deal_state': 'agree'})

    def button_agree_gh(self):
        vals = {'gap_deal_state': 'agree'}
        if self.evaluation_type == 'gap_deal':
            self._check_complete_evaluation()
            self.suspend_security()._create_development_plan()
            vals.update({'state_gap_deal': 'deal_close'})
        elif self.evaluation_type == 'development_plan':
            self._check_development_plan()
            self.suspend_security()._create_tracing_plan()
            vals.update({'state_gap_deal': 'agreed_plan'})
        else:
            self.validate_tracing_plan()
            vals.update({'state': 'finished'})
        self.write(vals)

    def button_agree_evaluation_evaluated(self):
        self._check_complete_evaluation()
        if self.gap_deal_state == 'no_deal':
            self.write({'gap_deal_state': 'agree_evaluated'})
        elif self.gap_deal_state == 'agree_leader':
            self.suspend_security()._create_development_plan()
            self.write({'state_gap_deal': 'deal_close', 'gap_deal_state': 'agree'})

    def button_agree_plan_leader(self):
        if self.evaluation_type == 'tracing_plan':
            self._check_at_least_one_tracing()
        else:
            self._check_development_plan()
        if self.gap_deal_state == 'no_deal':
            self.write({'gap_deal_state': 'agree_leader'})
        elif self.gap_deal_state == 'agree_evaluated':
            self._end_both_agree_states()

    def button_agree_plan_evaluated(self):
        if self.evaluation_type == 'tracing_plan':
            self._check_at_least_one_tracing()
        else:
            self._check_development_plan()
        if self.gap_deal_state == 'no_deal':
            self.write({'gap_deal_state': 'agree_evaluated'})
        elif self.gap_deal_state == 'agree_leader':
            self._end_both_agree_states()

    def _end_both_agree_states(self):
        if self.evaluation_type == 'tracing_plan':
            self.write({'state': 'finished', 'gap_deal_state': 'agree'})
        else:
            self.suspend_security()._create_tracing_plan()
            self.write({'state_gap_deal': 'agreed_plan', 'gap_deal_state': 'agree'})

    def button_go_back(self):
        if self.evaluation_type in ('gap_deal', 'development_plan'):
            vals = {'state_gap_deal': self.state_before_cancel,
                    'state_before_cancel': False,
                    'reason_cancel': False}
        else:
            vals = {'state': self.state_before_cancel,
                    'state_before_cancel': False,
                    'reason_cancel': False
                    }
        self.write(vals)

    # SE ELIMINA PORQUE YA NO ES NECESARIO
    # def button_cancel_gap_deal(self):
    #     for record in self:
    #         record.write({
    #             'reason_cancel': "Exonerado de Evaluación",
    #             'state_before_cancel': record.state_gap_deal,
    #             'state_gap_deal': 'canceled',
    #         })

    def action_cancel(self, is_canceled_by_employee_out=False):
        for record in self:
            vals = {
                'is_canceled_by_employee_out': is_canceled_by_employee_out,
                'reason_cancel': "Baja",
                'state_before_cancel': record.state,
                'state': 'canceled',
            }
            if record.evaluation_type in ['gap_deal', 'development_plan']:
                vals['state_gap_deal'] = 'canceled'
            else:
                vals['state'] = 'canceled'
            record.write(vals)

    def validate_tracing_plan(self):
        Tracing = self.env['onsc.desempeno.evaluation.tracing.plan'].sudo()
        if Tracing.search_count([('develop_means_id', 'in', self.tracing_plan_ids.development_means_ids.ids)]) == 0:
            raise ValidationError(
                _('Debe existir al menos un seguimiento ingresado para poder finalizar'))

    def _generate_environment_evaluations(self):
        Competency = self.env['onsc.desempeno.evaluation.competency'].suspend_security()
        Level = self.env['onsc.desempeno.level.line'].suspend_security()
        for rec in self:
            selected_random_environment = self.env['hr.employee']
            if len(rec.full_environment_ids) <= self.env.user.company_id.random_environment_evaluation_forms:
                random_environments = rec.full_environment_ids
            else:
                random_environments = random.sample(
                    rec.full_environment_ids,
                    self.env.user.company_id.random_environment_evaluation_forms
                )
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
                selected_random_environment |= random_environment.employee_id
                evaluation = self.suspend_security().create({
                    'current_job_id': rec.current_job_id.id,
                    'evaluator_current_job_id': random_environment.id,
                    'evaluated_id': rec.evaluated_id.id,
                    'evaluator_id': random_environment.employee_id.id,
                    # 'evaluator_uo_id': rec.evaluator_uo_id.id,
                    'evaluation_type': 'environment_evaluation',
                    'uo_id': rec.uo_id.id,
                    'inciso_id': rec.inciso_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                    'level_id': level_id.id,
                    'evaluation_stage_id': rec.evaluation_stage_id.id,
                    'general_cycle_id': rec.general_cycle_id.id,
                    'state_gap_deal': 'draft',
                })
                for skill in skills:
                    Competency.create({'evaluation_id': evaluation.id,
                                       'skill_id': skill.id,
                                       'skill_line_ids': [(6, 0, skill.skill_line_ids.filtered(
                                           lambda r: r.level_id.id == evaluation.level_id.id).ids)]
                                       })
            email_template_id = self.env.ref('onsc_desempeno.email_template_evaluacion_entorno')
            for partner in selected_random_environment.mapped('partner_id'):
                email_template_id.with_context(date_end=rec.sudo().evaluation_stage_id.end_date.strftime('%d-%m-%Y')).send_mail(
                    rec.id,
                    email_values={'email_to': partner.get_onsc_mails()}
                )
            rec.write({'environment_evaluation_ids': [(6, 0, selected_random_environment.ids)]})

    def _check_complete_evaluation(self):
        competencies = self.gap_deal_competency_ids if self.evaluation_type == 'gap_deal' else self.evaluation_competency_ids
        for competency in competencies:
            if not competency.degree_id or not competency.improvement_areas:
                raise ValidationError(
                    _('Deben estar todas las evaluaciones de competencias completas para poder continuar'))
        # for skill_line in competencies.mapped('evaluation_skill_line_ids'):
        #     if not skill_line.frequency_id:
        #         raise ValidationError(
        #             _('Deben estar todas las evaluaciones de competencias completas para poder continuar'))

    def _check_development_plan(self):
        if len(self.development_plan_ids.development_means_ids.ids) == 0:
            raise ValidationError(_('Deben tener al menos un plan de acción para poder acordar'))

    def notification_end_evaluation(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
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
            generated_form_email_template_id = self.env.ref(
                'onsc_desempeno.email_template_end_date_environment_definition')
            generated_form_email_template_id.send_mail(self.id, force_send=True)

        general_ids = GeneralCycle.search([('end_date_max', '=', date_end)]).ids
        count_message_deal = self.search_count(
            [('evaluation_type', 'in', ['gap_deal']), ('state_gap_deal', '!=', 'canceled'),
             ('year', '=', year),
             ('general_cycle_id', 'in', general_ids)])

        if count_message_deal > 0:
            generated_form_email_template_id = self.env.ref(
                'onsc_desempeno.email_template_end_date_gap_deal')
            generated_form_email_template_id.send_mail(self.id, force_send=True)

    def get_followers_mails(self):
        year = fields.Date.today().strftime('%Y')
        days_notification_end_ev = self.env.user.company_id.days_notification_end_ev
        date_end = fields.Date.today() + relativedelta(days=days_notification_end_ev)

        message_partner_ids = self.search(
            [('evaluation_type', 'in', ['environment_evaluation', 'collaborator']), ('state', '!=', 'canceled'),
             ('year', '=', year), ('evaluation_end_date', '=', date_end)]).mapped('evaluator_id.partner_id')

        return message_partner_ids.get_onsc_mails()

    def get_environment_definition_followers_mails(self):
        year = fields.Date.today().strftime('%Y')
        days_notification_end_ev = self.env.user.company_id.days_notification_end_ev
        date_end = fields.Date.today() + relativedelta(days=days_notification_end_ev)

        message_partner_ids = self.search(
            [('evaluation_type', '=', 'environment_definition'), ('state', '!=', 'canceled'),
             ('year', '=', year), ('environment_definition_end_date', '=', date_end)]).mapped('evaluated_id.partner_id')
        return message_partner_ids.get_onsc_mails()

    def get_gap_deal_followers_mails(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        year = fields.Date.today().strftime('%Y')
        days_notification_end_ev = self.env.user.company_id.days_notification_end_ev
        date_end = fields.Date.today() + relativedelta(days=days_notification_end_ev)
        general_ids = GeneralCycle.search([('end_date_max', '=', date_end)]).ids
        message_partner_ids = self.search(
            [('evaluation_type', '=', 'gap_deal'), ('state_gap_deal', '!=', 'canceled'),
             ('year', '=', year), ('general_cycle_id', 'in', general_ids)]).mapped('evaluator_id.partner_id')
        message_partner_ids |= self.search(
            [('evaluation_type', '=', 'gap_deal'), ('state_gap_deal', '!=', 'canceled'),
             ('year', '=', year), ('general_cycle_id.end_date_max', '=', date_end)]).mapped('evaluated_id.partner_id')
        return message_partner_ids.get_onsc_mails()

    def process_end_block_evaluation(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        general_ids = GeneralCycle.search([('end_date_max', '<=', fields.Date.today())]).ids

        for record in self.search([('general_cycle_id', 'in', general_ids),
                                   ('state', 'not in', ['canceled', 'finished', 'uncompleted']),
                                   ('evaluation_type', 'in', ['self_evaluation', 'leader_evaluation'])]):
            if record.state == 'completed':
                record.write({'state': 'finished'})
            else:
                record.write({'state': 'uncompleted'})

        for record in self.search([('evaluation_stage_id.active', '=', True),
                                   ('environment_definition_end_date', '<=', fields.Date.today()),
                                   ('state', 'not in', ['canceled', 'finished', 'uncompleted']),
                                   ('evaluation_type', 'in', ['environment_definition'])]):
            if record.state == 'completed':
                record.write({'state': 'finished'})
            else:
                record.write({'state': 'uncompleted'})

        self.search([
            ('evaluation_stage_id.active', '=', True),
            ('evaluation_end_date', '<=', fields.Date.today()),
            ('state', '!=', 'canceled'),
            ('locked', '!=', True),
            ('evaluation_type', 'in', ['environment_evaluation', 'collaborator'])]).write({'locked': True})

    def process_end_gap_deal(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        general_ids = GeneralCycle.search([('end_date_max', '<=', fields.Date.today())]).ids
        tracing_general_ids = GeneralCycle.search([('end_date', '<=', fields.Date.today())]).ids

        for record in self.search(
                [('general_cycle_id', 'in', general_ids),
                 ('state_gap_deal', 'not in', ['canceled']),
                 ('evaluation_type', 'in', ['gap_deal', 'development_plan'])]):

            if record.evaluation_type == 'development_plan':
                is_agreed_plan = record.state_gap_deal == 'agreed_plan'
            else:
                is_agreed_plan = record.state_gap_deal in ['deal_close', 'agreed_plan']

            if is_agreed_plan:
                record.write({'state_gap_deal': 'finished'})
            elif record.state_gap_deal not in ['finished', 'uncompleted']:
                record.write({'state_gap_deal': 'uncompleted'})

        for record in self.search(
                [('general_cycle_id', 'in', tracing_general_ids),
                 ('state', 'not in', ['finished', 'canceled']),
                 ('evaluation_type', 'in', ['tracing_plan'])]):
            if record.state in ['in_process'] and len(
                    record.tracing_plan_ids.tracing_means_ids.tracing_plan_ids.ids) > 0:
                record.write({'state': 'finished'})
            elif record.state not in ['finished', 'uncompleted']:
                record.write({'state': 'uncompleted'})

    def _create_development_plan(self):
        Job = self.env['hr.job'].sudo()
        Skill = self.env['onsc.desempeno.skill'].suspend_security()
        Competency = self.env['onsc.desempeno.evaluation.development.competency'].suspend_security()
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()

        valid_days = (self.general_cycle_id.end_date - fields.Date.from_string(fields.Date.today())).days
        if self.env.user.company_id.days_gap_develop_plan_creation < valid_days and self.state_gap_deal != 'canceled':
            evaluation = self.copy_data()
            evaluation[0]["evaluation_type"] = "development_plan"
            evaluation[0]["gap_deal_state"] = "no_deal"
            evaluation[0]["general_comments"] = False
            evaluation[0]["state_gap_deal"] = 'draft'
            evaluation[0]["current_job_id"] = self.current_job_id.id
            evaluation[0]["evaluator_current_job_id"] = self.evaluator_current_job_id.id
            if self.current_job_id:
                _department_id = self.current_job_id.department_id
                if _department_id.manager_id == self.current_job_id.employee_id:
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

                evaluation[0]["original_evaluator_id"] = False
                evaluation[0]["reason_change_id"] = False
                evaluation[0]["uo_id"] = self.current_job_id.department_id.id
            elif evaluation[0]["use_original_evaluator"] is True:
                evaluation[0]["evaluator_id"] = evaluation[0]["original_evaluator_id"]
                evaluation[0]["original_evaluator_id"] = False
                evaluation[0]["reason_change_id"] = False
            plan = Evaluation.with_context(gap_deal=True).create(evaluation)

            for competency in Skill.search([]):
                Competency.create({
                    'evaluation_id': plan.id,
                    'skill_id': competency.id,
                })
        else:
            self.write({'is_development_plan_not_generated': True})
        return True

    def _create_tracing_plan(self):
        Competency = self.env['onsc.desempeno.evaluation.development.competency'].suspend_security()
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        Job = self.env['hr.job'].sudo()

        evaluation = self.copy_data()
        evaluation[0]["evaluation_type"] = "tracing_plan"
        evaluation[0]["gap_deal_state"] = "no_deal"
        evaluation[0]["state"] = 'draft'
        evaluation[0]["state_gap_deal"] = 'draft'
        evaluation[0]["general_comments"] = False
        evaluation[0]["current_job_id"] = self.current_job_id.id
        evaluation[0]["evaluator_current_job_id"] = self.evaluator_current_job_id.id
        if self.current_job_id:
            _department_id = self.current_job_id.department_id
            if _department_id.manager_id == self.current_job_id.employee_id:
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

            evaluation[0]["original_evaluator_id"] = False
            evaluation[0]["reason_change_id"] = False
            evaluation[0]["uo_id"] = self.current_job_id.department_id.id
        elif evaluation[0]["use_original_evaluator"] is True:
            evaluation[0]["evaluator_id"] = evaluation[0]["original_evaluator_id"]
            evaluation[0]["original_evaluator_id"] = False
            evaluation[0]["reason_change_id"] = False

        tracing_plan = Evaluation.with_context(gap_deal=True).create(evaluation)
        for competency in self.development_plan_ids:
            tracing_means_vals = []
            for development_means_id in competency.development_means_ids:
                tracing_means_vals.append([0, 0, {
                    'comments': development_means_id.comments,
                    'agreed_activities': development_means_id.agreed_activities,
                    'detail_activities': development_means_id.detail_activities,
                    'means_id': development_means_id.means_id.id,
                }])
            Competency.create({
                'tracing_id': tracing_plan.id,
                'skill_id': competency.skill_id.id,
                'development_goal': competency.development_goal,
                'tracing_means_ids': tracing_means_vals
            })
        return True

    def get_end_gap_deal(self):
        year = fields.Date.today().strftime('%Y')
        general_cycle = self.search(
            [('evaluation_type', '=', 'gap_deal'), ('year', '=', year)], limit=1).mapped('general_cycle_id')
        return general_cycle.end_date_max.strftime('%d/%m/%Y')

    def get_evalaution_end_date(self):
        days_notification_end_ev = self.env.user.company_id.days_notification_end_ev
        date_end = fields.Date.today() + relativedelta(days=days_notification_end_ev)
        return date_end.strftime('%d/%m/%Y')
