# -*- coding: utf-8 -*-
from odoo import fields, models, tools


class ONSCLegajoDepartment(models.Model):
    _name = "onsc.legajo.department"
    _description = "Legajo - UO"
    _auto = False
    _inherit = "onsc.legajo.abstract.legajo.security"

    legajo_id = fields.Many2one('onsc.legajo', string="Legajo")
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    job_id = fields.Many2one('hr.job', string="Puesto")
    department_id = fields.Many2one('hr.department', string="UO")
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    legajo_state = fields.Selection([('active', 'Activo'), ('egresed', 'Egresado')], string='Estado del funcionario', )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT
    row_number() OVER (ORDER BY legajo.id, contract.id, job.id) AS id,
    legajo.id AS legajo_id,
    legajo.legajo_state,
    contract.id AS contract_id,
    job.id AS job_id,
    job.department_id,
    employee.id AS employee_id
FROM
    hr_contract contract
LEFT JOIN hr_job job ON job.contract_id = contract.id
JOIN onsc_legajo legajo ON contract.legajo_id = legajo.id
JOIN hr_employee employee ON legajo.employee_id = employee.id
)''' % (self._table,))

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador_legajo')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_ue')
