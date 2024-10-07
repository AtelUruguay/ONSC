# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api
from odoo.osv import expression


class ONSCLegajoDepartment(models.Model):
    _name = "onsc.legajo.department"
    _description = "Legajo - UO"
    _auto = False
    _order = "legajo_id"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            # is_legajo_id_in_base_args = False
            # for arg in args:
            #     if (isinstance(arg, tuple) or isinstance(arg, list)) and len(arg) and arg[0] == 'legajo_id':
            #         is_legajo_id_in_base_args = True
            # if not is_legajo_id_in_base_args:
            args = self._get_domain(args)
        return super(ONSCLegajoDepartment, self.with_context(avoid_recursion=True))._search(args, offset=offset,
                                                                                            limit=limit, order=order,
                                                                                            count=count,
                                                                                            access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            domain = self._get_domain(domain)
        return super(ONSCLegajoDepartment, self.with_context(avoid_recursion=True)).read_group(domain, fields, groupby,
                                                                                               offset=offset,
                                                                                               limit=limit,
                                                                                               orderby=orderby,
                                                                                               lazy=lazy)

    def _is_group_responsable_uo_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo')

    def _get_domain(self, args):
        is_config_security = self.user_has_groups(
            'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_hr_ue')

        if is_config_security:
            contract_ids = self._get_contract_ids()
            args = expression.AND([[
                ('contract_id', 'in', contract_ids),
            ], args])
        elif is_inciso_security:
            contract_ids = self._get_contract_ids()
            contract = self.env.user.employee_id.job_id.contract_id
            args = expression.AND([[
                ('contract_id', 'in', contract_ids),
                ('inciso_id', '=', contract.inciso_id.id)
            ], args])
        elif is_ue_security:
            contract_ids = self._get_contract_ids()
            contract = self.env.user.employee_id.job_id.contract_id
            args = expression.AND([[
                ('contract_id', 'in', contract_ids),
                ('operating_unit_id', '=', contract.operating_unit_id.id)
            ], args])
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            new_args = [
                ('department_id', 'in', department_ids),

                ('type', '=', 'active'),
            ]
            user_employee = self.env.user.employee_id
            if user_employee:
                new_args.append((('employee_id', '!=', user_employee.id)))
            args = expression.AND([new_args, args])
        return args

    def _get_contract_ids(self):
        available_contracts = self.env['onsc.legajo']._get_user_available_contract()
        return available_contracts.ids

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoDepartment, self).fields_get(allfields, attributes)
        hide = ['end_date', 'employee_id', 'job_id', 'type', 'active_job_qty', 'start_date']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    legajo_id = fields.Many2one('onsc.legajo', string="Funcionario")
    contract_id = fields.Many2one('hr.contract', string="Contrato")
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
    type = fields.Selection(
        string='Tipo',
        selection=[('active', 'Activo'),
                   ('egresed', 'Egresado')],
        required=False)

    active_job_qty = fields.Integer(string='Cantidad de puestos activos (por Legajo)')
    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen')
    operating_unit_origin_id = fields.Many2one("operating.unit",
                                               string="Unidad ejecutora origen")
    inciso_dest_id = fields.Many2one('onsc.catalog.inciso', string='Inciso destino', history=True)
    operating_unit_dest_id = fields.Many2one("operating.unit",
                                             string="Unidad ejecutora Destino")
    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?')
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')
    nro_doc = fields.Char(u'Número de documento')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT
row_number() OVER(ORDER BY legajo_id, contract_id, type, job_id) AS id, *
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
    contract.nro_doc
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
    contract.nro_doc
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
    contract.nro_doc
FROM
    hr_contract contract WHERE legajo_id IS NOT NULL) AS base_contract_view
WHERE contract_legajo_state = 'outgoing_commission') AS main_query)''' % (self._table,))

    def get_uo_tree(self, contract=False):
        Department = self.env['hr.department'].sudo()
        department_ids = []
        if self.user_has_groups('onsc_legajo.group_legajo_hr_inciso,onsc_legajo.group_legajo_hr_ue'):
            contract_id = contract or self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            args = []
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    ('operating_unit_id', '=', operating_unit_id.id)
                ], args])
            department_ids = Department.search(args).ids
        elif self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo'):
            department_id = self.env.user.employee_id.job_id.department_id.id
            department_ids = Department.search(['|', ('id', 'child_of', department_id),
                                                ('id', '=', department_id)]).ids
        return department_ids

    def button_open_legajo(self):
        ctx = self.env.context.copy()
        ctx.update({'edit': False})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'onsc.legajo',
            'name': 'Ver legajo',
            'context': ctx,
            "target": "current",
            "res_id": self.legajo_id.id,
        }
