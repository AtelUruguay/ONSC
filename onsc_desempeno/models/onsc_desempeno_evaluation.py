# -*- coding: utf-8 -*-
import logging

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

    def _get_domain(self, args):
        if self._context.get('self_evaluation'):
            args = self._get_domain_evaluation(args, 'self_evaluation')
        if self._context.get('collaborator_evaluation'):
            args = self._get_domain_collaborator(args)
        if self._context.get('leader_evaluation'):

            collaborators = [x for x in args if x[0] == 'collaborators' and x[2] is True]
            if not collaborators:

                department_id = self.env.user.employee_id.job_id.department_id.id
                manager_ids = self.env['hr.department'].search(['|',
                                                                ('id', 'child_of', department_id),
                                                                ('id', '=', department_id)]).manager_id.ids
                args = expression.AND([[('evaluator_id', 'in', manager_ids), ], args])
            else:
                args.remove(collaborators[0])
                args = expression.AND([[('evaluator_id', '=', self.env.user.employee_id.id)], args])
            args = self._get_domain_evaluation(args, 'leader_evaluation')

        if self._context.get('environment_definition'):
            args = self._get_domain_evaluation(args, 'environment_definition')

        return args

    def _get_domain_evaluation(self, args, evaluation_type):
        abstract_security = self._is_group_admin_gh_inciso() or self._is_group_admin_gh_ue()
        if self._is_group_admin_gh_inciso():
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
            args = expression.AND([[('inciso_id', '=', inciso_id), ('evaluation_type', '=', evaluation_type)], args])
        elif self._is_group_admin_gh_ue():
            operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
            args = expression.AND(
                [[('operating_unit_id', '=', operating_unit_id), ('evaluation_type', '=', evaluation_type)], args])
        elif self._is_group_usuario_evaluacion():
            if not abstract_security:
                args = expression.AND(
                    [[('evaluation_type', '=', evaluation_type)],
                     args])
            else:
                args = expression.OR(
                    [[('evaluation_type', '=', evaluation_type)],
                     args])
        return args

    def _get_domain_collaborator(self, args):
        abstract_security = self._is_group_admin_gh_inciso() or self._is_group_admin_gh_ue() or self._is_group_responsable_uo()
        if self._is_group_responsable_uo():
            user_department = self.env['hr.department'].search([('manager_id', '=', self.env.user.employee_id.id)])
            available_department_ids = []
            available_department_ids.extend(user_department.ids)
            for user_department in user_department:
                available_department_ids.extend(
                    self.env['hr.department'].search([('id', 'child_of', user_department.id)]).ids)
            args = expression.AND([[('evaluated_id', '!=', self.env.user.employee_id.id),
                                    ('uo_id', 'in', available_department_ids),
                                    ('evaluation_type', '=', 'collaborator')], args])
        elif self._is_group_admin_gh_inciso():
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
            args = expression.AND([[('evaluated_id', '!=', self.env.user.employee_id.id), ('inciso_id', '=', inciso_id),
                                    ('evaluation_type', '=', 'collaborator')], args])
        elif self._is_group_admin_gh_ue():
            operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
            args = expression.AND([[('evaluated_id', '!=', self.env.user.employee_id.id),
                                    ('operating_unit_id', '=', operating_unit_id),
                                    ('evaluation_type', '=', 'collaborator')], args])
        elif self._is_group_usuario_evaluacion():
            if not abstract_security:
                args = expression.AND(
                    [[('evaluator_id', '=', self.env.user.employee_id.id), ('evaluation_type', '=', 'collaborator')],
                     args])
            else:
                args = expression.OR(
                    [[('evaluator_id', '=', self.env.user.employee_id.id), ('evaluation_type', '=', 'collaborator')],
                     args])
        args2 = [('original_evaluator_id', '=', self.env.user.employee_id.id), ('evaluation_type', '=', 'collaborator')]
        return expression.OR([args2, args])

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
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador', readonly=True)
    original_evaluator_id = fields.Many2one('hr.employee', string='Evaluador Original', readonly=True)
    environment_evaluation_ids = fields.Many2many('hr.employee', 'enviroment_evaluator_evaluation_rel', 'evaluation_id',
                                                  'enviroment_evaluator_id', string='Evaluación de Entorno',
                                                  readonly=True)
    environment_ids = fields.Many2many('hr.employee', 'enviroment_evaluation_rel', 'evaluation_id', 'enviroment_id',
                                       string='Entorno')
    uo_id = fields.Many2one('hr.department', string='UO', readonly=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='UE', readonly=True)
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', readonly=True)
    level_id = fields.Many2one('onsc.desempeno.level', string='Nivel', readonly=True)
    evaluation_stage_id = fields.Many2one('onsc.desempeno.evaluation.stage', string='Evaluación 360', readonly=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', readonly=True)
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
