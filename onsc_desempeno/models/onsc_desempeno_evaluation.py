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
    _description = u'Evaluación'

    def _get_domain(self, args):
        if self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id

            args = expression.AND([[('inciso_id', '=', inciso_id), ], args])
        elif self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue'):
            operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
            args = expression.AND([[('operating_unit_id', '=', operating_unit_id), ], args])
        elif self.user_has_groups('onsc_desempeno.group_desempeno_usuario_evaluacion'):
            args = expression.OR([[('evaluated_id', '=', self.env.user.employee_id.id), ], args])

        return args

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
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', required=True)
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
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', readonly=True)
    year = fields.Integer(tring='Año a Evaluar', readonly=True, related='general_cycle_id.year')
    evaluation_start_date = fields.Date(string='Fecha inicio ciclo evaluación', readonly=True)
    evaluation_end_date = fields.Date(string='Fecha fin ciclo evaluación', readonly=True)
    environment_definition_end_date = fields.Date(string='Fecha de Fin de la Definición de Entorno', readonly=True)
    evaluation_competency_ids = fields.One2many('onsc.desempeno.evaluation.competency', 'evaluation_id',
                                                string='Evaluación de Competencias')
    general_comments = fields.Text(string='Comentarios Generales')
    state = fields.Selection(STATE, string='Estado', default='draft', readonly=True)
    locked = fields.Boolean(string='Bloqueado')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    change_evaluator = fields.Boolean(string="Cambio de evaluador", default=False)
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

    @api.depends('evaluated_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            if record.evaluated_id and record.general_cycle_id:
                record.name = '%s - %s' % (record.evaluated_id.name, record.general_cycle_id.year)
            else:
                record.name = ''

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.evaluation_type == 'self_evaluation' and (record.state not in ['in_process'] or record.evaluated_id.id != self.env.user.employee_id.id)

    @api.depends('state')
    def _compute_evaluation_form_edit(self):
        for record in self:
            record.evaluation_form_edit = record.evaluation_type == 'self_evaluation' and record.evaluated_id.id == self.env.user.employee_id.id

    def button_start_evaluation(self):
        self.write({'state': 'in_process'})

    def button_completed_evaluation(self):
        self._check_complete_evaluation()
        self.write({'state': 'completed'})

    def _check_complete_evaluation(self):
        if self.evaluation_type != 'environment_definition' and not self.general_comments:
            raise ValidationError(_("El campo comentarios generales es obligatorio"))

        for competency in self.evaluation_competency_ids:
            if not competency.degree_id or not competency.improvement_areas:
                raise ValidationError(
                    _('Deben estar todas las evaluaciones de competencias completas para poder pasar a "Completado"'))
