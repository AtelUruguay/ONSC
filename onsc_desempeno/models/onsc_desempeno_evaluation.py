# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_definition', 'Definición de entorno'),
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
    evaluation_start_date = fields.Date(string='Fecha de Inicio de la Evaluación', readonly=True)
    evaluation_end_date = fields.Date(string='Fecha de Fin de la Evaluación', readonly=True)
    environment_definition_end_date = fields.Date(string='Fecha de Fin de la Definición de Entorno', readonly=True)
    evaluation_compentecy_ids = fields.One2many('onsc.desempeno.evaluation.competency', 'evaluation_id',
                                                string='Evaluación de Competencias')
    general_comments = fields.Text(string='Comentarios Generales', readonly=True,
                                   states={'in_progress': [('readonly', False)]})
    state = fields.Selection(STATE, string='Estado', default='draft', readonly=True)
    locked = fields.Boolean(string='Bloqueado')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    change_evaluator = fields.Boolean(string="Cambio de evaluador")
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

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['in_process']
