# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.osv import expression

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_definition', 'Definición de entorno'),
    ('gap_deal', 'Acuerdo de Brecha'),
    ('development_plan', 'Plan de desarrollo'),
    ('tracing_plan', 'Seguimiento del Plan de desarrollo'),
    ('collaborator_consolidate', 'Consolidado de colaborador'),
    ('environment_consolidate', 'Consolidado de entorno'), ]

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


class ONSCDesempenoEvaluationReport(models.Model):
    _name = "onsc.desempeno.evaluation.report"
    _description = "Reporte y Consulta General de Ciclo de Evaluación "

    def _is_group_admin_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso')

    def _is_group_admin_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue')

    def _get_domain_evaluation(self, args):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        args_extended = expression.AND([[('user_id', '=', self.env.user.id)], args])
        if self._is_group_admin_gh_inciso():
            args_extended = expression.AND([[('inciso_id', '=', inciso_id)], args_extended])
        elif self._is_group_admin_gh_ue() and not self._is_group_admin_gh_inciso():
            args_extended = expression.AND([[('operating_unit_id', '=', operating_unit_id)], args_extended])
        return args_extended

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        args = self._get_domain_evaluation(args)
        return super(ONSCDesempenoEvaluationReport, self)._search(args, offset=offset, limit=limit, order=order,
                                                                  count=count, access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        domain = self._get_domain_evaluation(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    operating_unit_id = fields.Many2one('operating.unit', string='UE', ondelete='cascade')
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año a Evaluar', ondelete='cascade')
    evaluation_type = fields.Selection(EVALUATION_TYPE, string='Tipo', )
    evaluation_type_display_name = fields.Char(
        string='String del Tipo',
        compute='_compute_evaluation_type_display_name',
    )
    state = fields.Selection(STATE, string='Estado', )
    state_display_name = fields.Char(
        string='String del Estado',
        compute='_compute_state_display_name',
    )
    gap_deal_state = fields.Selection(selection=GAP_DEAL_STATES, string="Subestado")
    evaluated_id = fields.Many2one('hr.employee', string='Evaluado', ondelete='cascade')
    evaluator_id = fields.Many2one('hr.employee', string='Evaluador', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Usuario', readonly=True, ondelete='cascade')
    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación', ondelete='cascade')
    consolidated_id = fields.Many2one('onsc.desempeno.consolidated', string='Consolidado', ondelete='cascade')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', readonly=True, ondelete='cascade')
    show_button_evaluation = fields.Boolean('Ver botón Ver evaluaciones', compute='_compute_show_button_evaluation')

    @api.depends('evaluation_type')
    def _compute_evaluation_type_display_name(self):
        valid_attrs = dict(self._fields.get('evaluation_type').selection)
        for rec in self:
            rec.evaluation_type_display_name = valid_attrs.get(rec.evaluation_type, _('Desconocido'))

    @api.depends('state')
    def _compute_state_display_name(self):
        valid_attrs = dict(self._fields.get('state').selection)
        for rec in self:
            rec.state_display_name = valid_attrs.get(rec.state, _('Desconocido'))

    def button_open_evaluation(self):
        ctx = self.env.context.copy()
        ctx.update({'show_evaluation_type': True})
        if self.evaluation_type == 'collaborator_consolidate':
            ctx.update({'readonly_evaluation': True})
            action = \
                self.sudo().env.ref('onsc_desempeno.onsc_desempeno_collaborator_consolidated_readonly_action').read()[0]
            action.update({'res_id': self.consolidated_id.id, 'context': ctx, })
            return action
        elif self.evaluation_type == 'environment_consolidate':
            ctx.update({'readonly_evaluation': True})
            action = \
                self.sudo().env.ref('onsc_desempeno.onsc_desempeno_collaborator_consolidated_readonly_action').read()[0]
            action.update({'res_id': self.consolidated_id.id, 'context': ctx, })
            return action
        else:

            if self.evaluation_type in ['gap_deal', 'development_plan']:
                ctx.update({'readonly_evaluation': True, 'gap_deal': True})
            elif self.evaluation_type == 'tracing_plan':
                ctx.update({'readonly_evaluation': True, 'gap_deal': False, 'tracing_plan': True})
            else:
                ctx.update({'readonly_evaluation': True, 'gap_deal': False})

            if self.evaluation_type in ['development_plan', 'tracing_plan']:
                action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_devlop_action').read()[0]
            else:
                action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_evaluation_readonly_action').read()[0]
            action.update({'res_id': self.evaluation_id.id, 'context': ctx, })
            return action

    def buttton_export_xls(self):
        report = self.env['report.onsc.desempeno.evaluation.report'].with_context({
            'template_domain': [('res_model', '=', 'report.onsc.desempeno.evaluation.report'),
                                ('fname', '=', 'report_onsc_desempeno_evaluation_report.xlsx'),
                                ('gname', '=', False)]
        }).create({'results': [(6, 0, self.ids)]})
        report.report_xlsx()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            "res_id": report.id,
            'target': 'new',
            'res_model': 'report.onsc.desempeno.evaluation.report',
            'name': 'Descargar XLSX',
            'context': {'template_domain': [
                ('res_model', '=', 'report.onsc.desempeno.evaluation.report'),
                ('fname', '=', 'report_onsc_desempeno_evaluation_report.xlsx'),
                ('gname', '=', False)
            ]},
            'views': [[self.env.ref('onsc_desempeno.report_onsc_desempeno_evaluation_report').id, 'form']]
        }

    @api.depends('evaluation_type')
    def _compute_show_button_evaluation(self):
        group_admin = self._is_group_admin_gh_inciso() or self._is_group_admin_gh_ue()
        for record in self:
            if record.evaluation_type in ('environment_evaluation', 'collaborator',
                                          'leader_evaluation') and group_admin and record.evaluated_id.id == self.env.user.employee_id.id:
                condition = False
            else:
                condition = True
            record.show_button_evaluation = condition
