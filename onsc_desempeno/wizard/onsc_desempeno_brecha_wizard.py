# -*- coding: utf-8 -*-

import json

from odoo import fields, models, api

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('gap_deal', 'Acuerdo de Brecha'),
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


class ONSCOrganizationalWizard(models.TransientModel):
    _name = 'onsc.desempeno.brecha.wizard'
    _description = 'Competencias por brecha'

    def _is_group_desempeno_reportes(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_reportes')

    def _is_group_desempeno_admin_gh_inciso(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_inciso')

    def _is_group_desempeno_admin_gh_ue(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_admin_gh_ue')

    def _is_group_admin(self):
        return self.user_has_groups('onsc_desempeno.group_desempeno_administrador')

    @api.model
    def _default_general_cycle(self):
        year = fields.Date.today().strftime('%Y')
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        general_cycle_id = GeneralCycle.search([('year', '=', year)])
        return general_cycle_id.ids

    @api.model
    def _default_inciso(self):
        employee = self.env.user.employee_id
        if employee and employee.job_id and employee.job_id.contract_id and employee.job_id.contract_id.inciso_id:
            return employee.job_id.contract_id.inciso_id.ids
        return False

    @api.model
    def _default_operating_unit(self):
        employee = self.env.user.employee_id
        if employee and employee.job_id and employee.job_id.contract_id and employee.job_id.contract_id.operating_unit_id:
            return employee.job_id.contract_id.operating_unit_id.ids
        return False

    general_cycle_ids = fields.Many2many('onsc.desempeno.general.cycle', 'onsc_desempeno_brecha_cycle',
                                         'desempeno_brecha_id', 'desempeno_cycle_id', u'Año a evaluar',
                                         default=lambda self: self._default_general_cycle())
    inciso_ids = fields.Many2many('onsc.catalog.inciso', string=u'Inciso', default=lambda self: self._default_inciso())
    inciso_ids_domain = fields.Char(compute='_compute_inciso_ids_domain')
    inciso_edit = fields.Boolean('Puede editar el form?', compute='_compute_inciso_edit')
    operating_unit_ids = fields.Many2many('operating.unit', string=u'UE',
                                          default=lambda self: self._default_operating_unit())
    operating_unit_ids_domain = fields.Char(compute='_compute_operating_unit_ids_domain')
    operating_unit_edit = fields.Boolean('Puede editar el form?', compute='_compute_operating_unit_edit')
    uo_ids = fields.Many2many('hr.department', 'onsc_desempeno_brecha_department', 'desempeno_e_report_id',
                              'department_report_id', string=u'UO')
    uo_ids_domain = fields.Char(compute='_compute_uo_ids_domain')
    niveles_ids = fields.Many2many('onsc.desempeno.level', 'onsc_desempeno_brecha_level', 'desempeno_e_level_id',
                                   'level_report_id', u'Nivel del evaluado')
    evaluation_type = fields.Many2many('evaluation.type', string=u'Tipo evaluación')
    state = fields.Selection(STATE, string='Estado', )

    @api.depends('state')
    def _compute_inciso_ids_domain(self):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        for rec in self:
            if self._is_group_desempeno_reportes():
                all_inciso_ids = self.env['onsc.catalog.inciso'].search([]).ids
                domain = [('id', 'in', all_inciso_ids)]
            elif self._is_group_desempeno_admin_gh_inciso() or self._is_group_desempeno_admin_gh_ue():
                domain = [('id', '=', inciso_id)]
            else:
                domain = []
            rec.inciso_ids_domain = json.dumps(domain)

    @api.depends('inciso_ids')
    def _compute_operating_unit_ids_domain(self):
        OperatingUnit = self.env['operating.unit'].suspend_security()
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        for rec in self:
            if self._is_group_desempeno_admin_gh_inciso():
                if rec.inciso_ids:
                    operating_unit = OperatingUnit.suspend_security().search(
                        [('inciso_id', 'in', rec.inciso_ids.ids), ])
                    domain = [('id', 'in', operating_unit.ids)]
                else:
                    domain = [('id', '=', False)]
            elif self._is_group_desempeno_admin_gh_ue():
                domain = [('id', '=', operating_unit_id)]
            elif self._is_group_desempeno_reportes():
                all_operating_unit_ids = self.env['operating.unit'].search([]).ids
                domain = [('id', 'in', all_operating_unit_ids)]
            else:
                if rec.inciso_ids:
                    operating_unit = OperatingUnit.suspend_security().search([('inciso_id', 'in', rec.inciso_ids.ids)])
                    domain = [('id', 'in', operating_unit.ids)]
                else:
                    domain = [('id', 'in', [])]
            rec.operating_unit_ids_domain = json.dumps(domain)

    @api.depends('operating_unit_ids')
    def _compute_operating_unit_edit(self):
        for rec in self:
            if self._is_group_desempeno_admin_gh_inciso() or self._is_group_desempeno_reportes():
                rec.operating_unit_edit = True
            else:
                rec.operating_unit_edit = False

    @api.depends('inciso_ids')
    def _compute_inciso_edit(self):
        for rec in self:
            if self._is_group_desempeno_admin_gh_inciso() or self._is_group_desempeno_reportes():
                rec.inciso_edit = True
            else:
                rec.inciso_edit = False

    @api.depends('inciso_ids', 'operating_unit_ids')
    def _compute_uo_ids_domain(self):
        hrdepartment = self.env['hr.department'].suspend_security()
        for rec in self:
            domain = []
            if rec.inciso_ids or rec.operating_unit_ids:
                domain_conditions = []

                if rec.inciso_ids:
                    domain_conditions.append(('inciso_id', 'in', rec.inciso_ids.ids))
                if rec.operating_unit_ids:
                    domain_conditions.append(('operating_unit_id', 'in', rec.operating_unit_ids.ids))

                uos = hrdepartment.search(domain_conditions)
                domain = [('id', 'in', uos.ids)]
            else:
                domain = [('id', '=', False)]

            rec.uo_ids_domain = json.dumps(domain)

    def action_report_comp_brecha(self):
        where_clause = []
        if self.general_cycle_ids:
            cycle_ids_str = ", ".join(map(str, self.general_cycle_ids.ids))
            where_clause.append(f"onsc_e.general_cycle_id IN ({cycle_ids_str})")
        if self.inciso_ids:
            cycle_ids_str = ", ".join(map(str, self.inciso_ids.ids))
            where_clause.append(f"onsc_e.inciso_id IN ({cycle_ids_str})")
        if self.operating_unit_ids:
            cycle_ids_str = ", ".join(map(str, self.operating_unit_ids.ids))
            where_clause.append(f"onsc_e.operating_unit_id IN ({cycle_ids_str})")
        if self.uo_ids:
            cycle_ids_str = ", ".join(map(str, self.uo_ids.ids))
            where_clause.append(f"onsc_e.uo_id IN ({cycle_ids_str})")
        if self.niveles_ids:
            cycle_ids_str = ", ".join(map(str, self.niveles_ids.ids))
            where_clause.append(f"onsc_e.level_id IN ({cycle_ids_str})")
        if self.evaluation_type:
            id_to_value = {index + 1: et[0] for index, et in enumerate(EVALUATION_TYPE)}
            selected_types = [id_to_value[eval_id] for eval_id in self.evaluation_type.ids if eval_id in id_to_value]
            if selected_types:
                values_str = ", ".join(f"'{val}'" for val in selected_types)
                where_clause.append(f"onsc_e.evaluation_type IN ({values_str})")
        where_clause.append("""
            (
                (onsc_e.evaluation_type IN ('self_evaluation', 'leader_evaluation', 'collaborator', 'environment_evaluation')
                    AND onsc_e.state IN ('completed', 'finished'))
                OR
                (onsc_e.evaluation_type = 'gap_deal'
                    AND onsc_e.state_gap_deal IN ('deal_close', 'finished'))
            )
        """)
        where_clause_str = " AND ".join(where_clause)

        _query = f"""
            INSERT INTO report_competencia_brecha
                (comp_id, grado_id, inciso_id, operating_unit_id, uo_id,
                 general_cycle_id, evaluation_type, niveles_id, cant, porcent)
            SELECT
                onsc_ec.skill_id AS comp_id,
                onsc_ec.degree_id AS grado_id,
                onsc_e.inciso_id,
                onsc_e.operating_unit_id,
                onsc_e.uo_id,
                onsc_e.general_cycle_id,
                onsc_e.evaluation_type,
                onsc_e.level_id,
                COUNT(*) AS cant,
                0 as porcent
            FROM onsc_desempeno_evaluation AS onsc_e
                INNER JOIN onsc_desempeno_evaluation_competency AS onsc_ec
                ON onsc_e.id = onsc_ec.gap_deal_id or onsc_e.id = onsc_ec.evaluation_id
            WHERE {where_clause_str}
            GROUP BY
                onsc_ec.skill_id, onsc_ec.degree_id, onsc_e.inciso_id, onsc_e.operating_unit_id,
                onsc_e.uo_id, onsc_e.general_cycle_id, onsc_e.evaluation_type, onsc_e.level_id
        """
        cr = self.env.cr
        cr.execute("DELETE FROM report_competencia_brecha")
        cr.execute(_query)
        action = self.env.ref('onsc_desempeno.action_report_competencia_brecha').suspend_security().read()[0]
        action['target'] = 'main'
        return action


class EvaluationType(models.Model):
    _name = 'evaluation.type'
    _description = 'evaluation'

    name = fields.Char(u'Nombre de la opción')
    code = fields.Char(u'Código')
