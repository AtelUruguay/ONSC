# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api
from odoo.osv import expression
from odoo.tools import func


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
        result = super(ONSCLegajoDepartment, self.with_context(avoid_recursion=True)).read_group(domain, fields, groupby,
                                                                                                 offset=offset,
                                                                                                 limit=limit,
                                                                                                 orderby=orderby,
                                                                                                 lazy=lazy)
        for res in result:
            count_key, count_key_value = next(iter(res.items()))
            group_key_str = count_key.split('_count')[0]
            group_key = res.get(group_key_str)
            if not group_key:
                res[group_key_str] = (0, func.lazy(
                    lambda: self.fields_get().get(group_key_str).get('string') or 'Nivel'))
        return result

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
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel jerárquico")
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
    organigram_joker = fields.Many2one('hr.department', string='Organigrama')
    level_0 = fields.Many2one('hr.department', string='Nivel 0')
    level_1 = fields.Many2one('hr.department', string='Nivel 1')
    level_2 = fields.Many2one('hr.department', string='Nivel 2')
    level_3 = fields.Many2one('hr.department', string='Nivel 3')
    level_4 = fields.Many2one('hr.department', string='Nivel 4')
    level_5 = fields.Many2one('hr.department', string='Nivel 5')
    nro_doc = fields.Char(u'Número de documento')

    public_admin_entry_date = fields.Date(string=u'Fecha de ingreso AP')
    date_start_operating_unit = fields.Date(string=u'Fecha de ingreso UE')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
WITH base_contract_view AS (
    SELECT
        contract.legajo_id AS legajo_id,
        contract.id AS contract_id,
        contract.cs_contract_id,
        contract.legajo_state AS contract_legajo_state,
        contract.inciso_id,
        contract.operating_unit_id,
        contract.employee_id,
        contract.public_admin_entry_date,
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
        hr_contract contract
    WHERE
        legajo_id IS NOT NULL
),
hr_job_data AS (
    SELECT
        job.id AS job_id,
        job.name AS job_name,
        job.security_job_id AS security_job_id,
        job.department_id AS department_id,
        job.hierarchical_level_id,
        job.start_date AS start_date,
        job.end_date AS end_date,
        job.is_uo_manager,
        job.contract_id
    FROM
        hr_job job
    WHERE
        job.active = True AND (job.end_date IS NULL OR job.end_date > CURRENT_DATE)
),
last_job_data AS (
    SELECT DISTINCT ON (contract_id)
        job.id AS job_id,
        job.name AS job_name,
        job.security_job_id AS security_job_id,
        job.department_id AS department_id,
        job.hierarchical_level_id,
        job.start_date AS start_date,
        job.end_date AS end_date,
        job.is_uo_manager,
        job.contract_id
    FROM
        hr_job job
    ORDER BY
        job.contract_id, job.end_date DESC, job.id DESC
),
oldest_contract_data AS (
    SELECT
        contract.id AS contract_id,
        contract.operating_unit_id,
        contract.date_start,
        ROW_NUMBER() OVER (PARTITION BY contract.operating_unit_id ORDER BY contract.date_start ASC) AS rn
    FROM
        hr_contract contract
    WHERE
        contract.cs_contract_id IS NOT NULL
)
SELECT
    row_number() OVER(ORDER BY bc.legajo_id, bc.contract_id, bc.type, j.job_id) AS id,
    bc.*,
    jh.level_0 AS organigram_joker,
    jh.level_0,
    jh.level_1,
    jh.level_2,
    jh.level_3,
    jh.level_4,
    jh.level_5,
    j.job_id,
    j.job_name,
    j.security_job_id,
    j.department_id,
    j.hierarchical_level_id,
    j.start_date,
    j.end_date,
    j.is_uo_manager,
    ocd.date_start AS date_start_operating_unit
FROM base_contract_view bc
LEFT JOIN hr_job_data j
    ON bc.contract_id = j.contract_id AND bc.active_job_qty > 0
LEFT JOIN last_job_data ljd
    ON bc.contract_id = ljd.contract_id AND bc.active_job_qty = 0
LEFT JOIN onsc_legajo_job_hierarchy jh
    ON j.job_id = jh.job_id
LEFT JOIN oldest_contract_data ocd
    ON bc.contract_id = ocd.contract_id
WHERE
    bc.contract_legajo_state IN ('active', 'incoming_commission', 'reserved')
UNION ALL
SELECT
    row_number() OVER(ORDER BY bc.legajo_id, bc.contract_id, bc.type, ljd.job_id) AS id,
    bc.*,
    jh.level_0 AS organigram_joker,
    jh.level_0,
    jh.level_1,
    jh.level_2,
    jh.level_3,
    jh.level_4,
    jh.level_5,
    ljd.job_id,
    ljd.job_name,
    ljd.security_job_id,
    ljd.department_id,
    ljd.hierarchical_level_id,
    ljd.start_date,
    ljd.end_date,
    ljd.is_uo_manager,
    ocd.date_start AS date_start_operating_unit
FROM base_contract_view bc
LEFT JOIN last_job_data ljd
    ON bc.contract_id = ljd.contract_id
LEFT JOIN onsc_legajo_job_hierarchy jh
    ON ljd.job_id = jh.job_id
LEFT JOIN oldest_contract_data ocd
    ON bc.contract_id = ocd.contract_id
WHERE
    bc.contract_legajo_state = 'outgoing_commission'
)''' % (self._table,))

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
