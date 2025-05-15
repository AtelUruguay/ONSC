# -*- coding: utf-8 -*-
import logging
import uuid

from odoo import fields, models, api
from odoo.osv import expression

_logger = logging.getLogger(__name__)

CONSOLIDATED_TYPE = [
    ('environment', 'Consolidado de Entorno'),
    ('collaborator', 'Consolidado de Colaborador/a'), ]


class ONSCDesempenoConsolidated(models.Model):
    _name = 'onsc.desempeno.consolidated'
    _description = u'Consolidado'

    def _is_group_admin_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso')

    def _is_group_admin_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue')

    def _is_group_usuario_evaluacion(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_usuario_evaluacion')

    def _is_group_responsable_uo(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_responsable_uo')

    def _get_domain(self, args):
        if self._context.get('readonly_evaluation'):
            return args

        if self._context.get('collaborator'):
            evaluation_type = 'collaborator'
        elif self._context.get('environment'):
            evaluation_type = 'environment'

        collaborators = [x for x in args if x[0] == 'collaborators']
        evaluations = [x for x in args if x[0] == 'evaluations']
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id

        args_extended = [
            ('evaluation_type', '=', evaluation_type),
            ('evaluated_id', '=', self.env.user.employee_id.id),
            ('inciso_id', '=', inciso_id),
            ('operating_unit_id', '=', operating_unit_id)
        ]

        if not collaborators and not evaluations:
            if self._is_group_admin_gh_inciso():
                args_extended = expression.OR(
                    [[('inciso_id', '=', inciso_id), ('evaluation_type', '=', evaluation_type)], args_extended])
            elif self._is_group_admin_gh_ue():
                args_extended = expression.OR(
                    [[('operating_unit_id', '=', operating_unit_id), ('evaluation_type', '=', evaluation_type)],
                     args_extended])
            if self._is_group_responsable_uo():
                my_department = self.env.user.employee_id.job_id.department_id
                available_departments = my_department
                available_departments |= self.env['hr.department'].search([('id', 'child_of', my_department.id)])
                args_extended = expression.OR([[('evaluated_id', '!=', self.env.user.employee_id.id),
                                                ('uo_id', 'in', available_departments.ids),
                                                ('evaluation_type', '=', evaluation_type)], args_extended])
        return expression.AND([args_extended, args])

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_consolidated_menu') and self._context.get('ignore_security_rules',
                                                                                False) is False:
            args = self._get_domain(args)
        return super(ONSCDesempenoConsolidated, self)._search(args, offset=offset, limit=limit, order=order,
                                                              count=count,
                                                              access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_consolidated_menu') and self._context.get('ignore_security_rules',
                                                                                False) is False:
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    name = fields.Char(string="Nombre", compute="_compute_name", store=True)
    evaluation_type = fields.Selection(CONSOLIDATED_TYPE, string='Tipo', required=True, readonly=True)
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado', readonly=True)
    evaluator_ids = fields.Many2many('hr.employee', string='Evaluadores', readonly=True)
    active = fields.Boolean(string='Activo', default=True)

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='UE', readonly=True)
    uo_id = fields.Many2one('hr.department', string='UO', readonly=True)
    current_job_id = fields.Many2one(
        'hr.job',
        copy=False,
        string='Puesto actual',
        help=u'Usado para en caso de cambio de puesto saber el Puesto actual '
             'en el que se encuentra el Funcionario')
    level_id = fields.Many2one('onsc.desempeno.level', string='Nivel', readonly=True)
    evaluation_stage_id = fields.Many2one('onsc.desempeno.evaluation.stage', string='Evaluación 360', readonly=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', readonly=True)
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
    evaluation_competency_ids = fields.One2many('onsc.desempeno.evaluation.competency', 'consolidate_id',
                                                string='Evaluación de Competencias')
    is_gap_deal_not_generated = fields.Boolean(string='Acuerdo de brecha no generado')
    collaborators = fields.Boolean(string="Colaboradores directos", default=False)
    evaluations = fields.Boolean(string="Mis evaluaciones", default=False)
    is_pilot = fields.Boolean(string='¿Es piloto?', copy=False, related="general_cycle_id.is_pilot", store=True)
    comment_ids = fields.One2many(
        comodel_name='onsc.desempeno.consolidated.comment',
        inverse_name='consolidated_id',
        string='Comentarios generales'
    )

    @api.depends('evaluated_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            if record.evaluated_id and record.general_cycle_id:
                record.name = '%s - %s' % (record.evaluated_id.name, record.general_cycle_id.year)
            else:
                record.name = ''

    def button_show_info(self):
        user_id = self.env.user.id
        token = " '%s' " % (str(uuid.uuid4()))
        where_clause_str = " cons.id = %s " % (self.id)

        _query = f"""
                   INSERT INTO onsc_desempeno_competency_skills
                       (skill_id,dimension_id,behavior, frequency_id,improvement_areas,degree_id,token,report_user_id)
                   SELECT comp.skill_id,line.dimension_id,behavior,null as frequency_id,comp.improvement_areas,comp.degree_id,{token},{user_id}
                   FROM onsc_desempeno_consolidated cons  
                   LEFT JOIN  onsc_desempeno_evaluation_competency comp ON cons.id = comp.consolidate_id
                   LEFT JOIN competency_skill_line_rel rel ON comp.id =onsc_desempeno_evaluation_competency_id
                   LEFT JOIN onsc_desempeno_skill_line line ON rel.onsc_desempeno_skill_line_id = line.id
                   WHERE {where_clause_str} and cons.is_pilot = true
                   UNION ALL
                   SELECT   comp.skill_id,line.dimension_id,behavior,frequency_id,comp.improvement_areas,comp.degree_id,{token},{user_id}
                   FROM onsc_desempeno_consolidated cons  
                   LEFT JOIN onsc_desempeno_evaluation_competency comp ON cons.id = comp.consolidate_id
                   LEFT JOIN evaluation_competency_skill_line_rel rel ON  comp.id =onsc_desempeno_evaluation_competency_id
                   LEFT JOIN onsc_desempeno_evaluation_skill_line line ON rel.onsc_desempeno_evaluation_skill_line_id = line.id
                   WHERE {where_clause_str} and cons.is_pilot = false
               """
        cr = self.env.cr
        cr.execute('''DELETE FROM onsc_desempeno_competency_skills WHERE report_user_id = %s''' % (user_id,))
        cr.execute(_query)

        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_competency_skills_action').read()[0]
        return action


class ONSCDesempenoConsolidatedComment(models.Model):
    _name = 'onsc.desempeno.consolidated.comment'
    _description = u'Consolidado-Comentarios'
    _order = 'sequence'

    name = fields.Text(string="Comentario", required=True)
    sequence = fields.Integer(string='Orden', required=True)
    consolidated_id = fields.Many2one(
        'onsc.desempeno.consolidated',
        string='Consolidado',
        required=True,
        ondelete='cascade'
    )
