# -*- coding: utf-8 -*-

from odoo import fields, models, tools


class ONSCLegajoBaseView(models.Model):
    _name = "onsc.legajo.base.view"
    _description = "Legajo Vista Base"
    _auto = False
    _order = "legajo_id"
    legajo_id = fields.Many2one('onsc.legajo', string="Funcionario")
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado del funcionario',
    )
    contract_legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato')
    job_id = fields.Many2one('hr.job', string="Puesto")
    job_name = fields.Char(
        string='Nombre del puesto',
        required=False)
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    department_id = fields.Many2one('hr.department', string="UO")
    start_date = fields.Date(string='Fecha desde')
    end_date = fields.Date(string='Fecha hasta')
    active_job_qty = fields.Integer(string='Cantidad de puestos activos (por Legajo)')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT
    contract.legajo_id,
    contract.id AS contract_id,
    legajo.legajo_state AS legajo_state,
    contract.legajo_state AS contract_legajo_state,
    job.id AS job_id,
    job.name AS job_name,
    job.security_job_id AS security_job_id,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    job.department_id,
    job.start_date AS start_date,
    job.end_date AS end_date,
    'system' AS type,
    (SELECT COUNT(id) FROM hr_job WHERE active = True AND (end_date IS NULL OR end_date > CURRENT_DATE) AND legajo_id = legajo.id) AS active_job_qty
FROM
    hr_contract contract
LEFT JOIN hr_job job ON job.contract_id = contract.id
LEFT JOIN onsc_legajo legajo ON contract.legajo_id = legajo.id
WHERE
    (job.start_date <= CURRENT_DATE AND (job.end_date IS NULL OR job.end_date >= CURRENT_DATE)) OR
    job.id IS NULL AND contract.legajo_state <> 'baja'
)''' % (self._table,))
