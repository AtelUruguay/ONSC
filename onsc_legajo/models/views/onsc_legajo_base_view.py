# -*- coding: utf-8 -*-

from odoo import fields, models, tools


class ONSCLegajoBaseView(models.Model):
    _name = "onsc.legajo.base.view"
    _description = "Legajo Vista Base"
    _auto = False

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT
row_number() OVER(ORDER BY legajo_id, contract_id, type, main_query.job_id) AS id, *
FROM
--CONTRATO ACTIVO SIN PUESTOS ACTIVOS
(SELECT
    base_contract_view.*,
    NULL AS job_id,
    NULL AS job_name,
    NULL AS security_job_id,
    NULL AS department_id,
    NULL AS start_date,
    NULL AS end_date,
    NULL AS is_uo_manager
FROM
(SELECT
    contract.legajo_id AS legajo_id,
    contract.id AS contract_id,
    contract.legajo_state AS contract_legajo_state,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    'active' AS type,
    (SELECT COUNT(id) FROM hr_job WHERE active = True AND (end_date IS NULL OR end_date > CURRENT_DATE) AND contract_id = contract.id) AS active_job_qty,
    contract.inciso_origin_id AS inciso_origin_id,
    contract.operating_unit_origin_id AS operating_unit_origin_id,
    contract.inciso_dest_id AS inciso_dest_id,
    contract.operating_unit_dest_id AS operating_unit_dest_id,
    contract.regime_id AS regime_id,
    contract.commission_regime_id AS commission_regime_id,
    contract.descriptor1_id AS descriptor1_id,
    contract.descriptor2_id AS descriptor2_id,
    contract.descriptor3_id AS descriptor3_id,
    contract.descriptor4_id AS descriptor4_id,
    contract.nro_doc,
    contract.create_date AS contract_create_date
FROM
    hr_contract contract WHERE legajo_id IS NOT NULL) AS base_contract_view
WHERE contract_legajo_state IN ('active','incoming_commission','reserved') AND active_job_qty = 0
UNION ALL
--CONTRATO ACTIVO CON PUESTOS ACTIVOS
SELECT
    base_contract_view.*,
    hr_job.id AS job_id,
    hr_job.name AS job_name,
    hr_job.security_job_id AS security_job_id,
    hr_job.department_id AS department_id,
    hr_job.start_date AS start_date,
    hr_job.end_date AS end_date,
    hr_job.is_uo_manager as is_uo_manager
FROM
 (SELECT
    contract.legajo_id AS legajo_id,
    contract.id AS contract_id,
    contract.legajo_state AS contract_legajo_state,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    'active' AS type,
    (SELECT COUNT(id) FROM hr_job WHERE active = True AND (end_date IS NULL OR end_date > CURRENT_DATE) AND contract_id = contract.id) AS active_job_qty,
    contract.inciso_origin_id AS inciso_origin_id,
    contract.operating_unit_origin_id AS operating_unit_origin_id,
    contract.inciso_dest_id AS inciso_dest_id,
    contract.operating_unit_dest_id AS operating_unit_dest_id,
    contract.regime_id AS regime_id,
    contract.commission_regime_id AS commission_regime_id,
    contract.descriptor1_id AS descriptor1_id,
    contract.descriptor2_id AS descriptor2_id,
    contract.descriptor3_id AS descriptor3_id,
    contract.descriptor4_id AS descriptor4_id,
    contract.nro_doc,
    contract.create_date AS contract_create_date
FROM
    hr_contract contract WHERE legajo_id IS NOT NULL) AS base_contract_view
LEFT JOIN hr_job ON hr_job.contract_id = base_contract_view.contract_id
WHERE contract_legajo_state IN ('active','incoming_commission','reserved') AND active_job_qty > 0 AND (end_date IS NULL OR end_date > CURRENT_DATE)
--CONTRATO SALIENTE TOMAR EL ULTIMO PUESTO
UNION ALL
SELECT
    base_contract_view.*,
    (SELECT id FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS job_id,
    (SELECT name FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS job_name,
    (SELECT security_job_id FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS security_job_id,
    (SELECT department_id FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS department_id,
    (SELECT start_date FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS start_date,
    (SELECT end_date FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS end_date,
    (SELECT is_uo_manager FROM hr_job WHERE contract_id = base_contract_view.contract_id ORDER BY end_date DESC, id DESC limit 1) AS is_uo_manager
FROM
(SELECT
    contract.legajo_id AS legajo_id,
    contract.id AS contract_id,
    contract.legajo_state AS contract_legajo_state,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    'active' AS type,
    (SELECT COUNT(id) FROM hr_job WHERE active = True AND (end_date IS NULL OR end_date > CURRENT_DATE) AND contract_id = contract.id) AS active_job_qty,
    contract.inciso_origin_id AS inciso_origin_id,
    contract.operating_unit_origin_id AS operating_unit_origin_id,
    contract.inciso_dest_id AS inciso_dest_id,
    contract.operating_unit_dest_id AS operating_unit_dest_id,
    contract.regime_id AS regime_id,
    contract.commission_regime_id AS commission_regime_id,
    contract.descriptor1_id AS descriptor1_id,
    contract.descriptor2_id AS descriptor2_id,
    contract.descriptor3_id AS descriptor3_id,
    contract.descriptor4_id AS descriptor4_id,
    contract.nro_doc,
    contract.create_date AS contract_create_date
FROM
    hr_contract contract WHERE legajo_id IS NOT NULL) AS base_contract_view
WHERE contract_legajo_state = 'outgoing_commission') AS main_query)''' % (self._table,))
