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
            if self._context.get('is_from_padron_report'):
                args = self._get_padron_domain(args)
            else:
                args = self._get_domain(args)
        return super(ONSCLegajoDepartment, self.with_context(avoid_recursion=True))._search(args, offset=offset,
                                                                                            limit=limit, order=order,
                                                                                            count=count,
                                                                                            access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            if self._context.get('is_from_padron_report'):
                domain = self._get_padron_domain(domain)
            else:
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

    def _get_padron_domain(self, args):
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')
        inciso_id = self._context.get('inciso_id', False)
        operating_unit_id = self._context.get('operating_unit_id', False)
        if not inciso_id and not operating_unit_id:
            return expression.AND([[(True,'=',False)], args])

        if is_inciso_security:
            contract_ids = self._get_contract_ids()
            new_args = [
                ('contract_id', 'in', contract_ids),
                ('inciso_id', '=', inciso_id)
            ]
            if operating_unit_id:
                new_args.append(('operating_unit_id', '=', operating_unit_id))
            args = expression.AND([new_args, args])
        elif is_ue_security:
            contract_ids = self._get_contract_ids()
            args = expression.AND([[
                ('contract_id', 'in', contract_ids),
                ('operating_unit_id', '=', operating_unit_id)
            ], args])
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
    first_operating_unit_entry_date = fields.Date(string=u'Fecha de ingreso UE')

    date_end = fields.Date(string=u'Fecha baja')
    date_to = fields.Date(string=u'Fecha hasta')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
WITH base_contract_view AS (
    SELECT
        contract.legajo_id,
        contract.id AS contract_id,
        contract.legajo_state AS contract_legajo_state,
        contract.inciso_id,
        contract.operating_unit_id,
        contract.employee_id,
        'active' AS type,
        contract.inciso_origin_id,
        contract.operating_unit_origin_id,
        contract.inciso_dest_id,
        contract.operating_unit_dest_id,
        contract.regime_id,
        contract.commission_regime_id,
        contract.descriptor1_id,
        contract.descriptor2_id,
        contract.descriptor3_id,
        contract.descriptor4_id,
        contract.nro_doc,
        contract.public_admin_entry_date,
        contract.first_operating_unit_entry_date,
        contract.date_end,
        contract.date_end_commission,
        COUNT(hr_job.id) FILTER (WHERE hr_job.active AND (hr_job.end_date IS NULL OR hr_job.end_date > CURRENT_DATE)) AS active_job_qty
    FROM hr_contract contract
    LEFT JOIN hr_job ON hr_job.contract_id = contract.id
    WHERE contract.legajo_id IS NOT NULL
    GROUP BY contract.id
)
SELECT
    ROW_NUMBER() OVER(ORDER BY main_query.legajo_id, main_query.contract_id, main_query.type, main_query.job_id) AS id,
    main_query.*,
    jh.level_0 AS organigram_joker,
    jh.level_0,
    jh.level_1,
    jh.level_2,
    jh.level_3,
    jh.level_4,
    jh.level_5
FROM (
    -- CONTRATO ACTIVO SIN PUESTOS
    SELECT
        bc.*,
        NULL AS job_id,
        NULL AS job_name,
        NULL AS security_job_id,
        NULL AS department_id,
        NULL AS hierarchical_level_id,
        NULL AS start_date,
        NULL AS end_date,
        NULL AS is_uo_manager
    FROM base_contract_view bc
    WHERE bc.contract_legajo_state IN ('active','incoming_commission','reserved') AND bc.active_job_qty = 0

    UNION ALL

    -- CONTRATO ACTIVO CON PUESTOS ACTIVOS
    SELECT
        bc.*, j.id AS job_id, j.name AS job_name, j.security_job_id, j.department_id,
        j.hierarchical_level_id, j.start_date, j.end_date, j.is_uo_manager
    FROM base_contract_view bc
    JOIN hr_job j ON j.contract_id = bc.contract_id
    WHERE bc.contract_legajo_state IN ('active','incoming_commission','reserved')
        AND bc.active_job_qty > 0
        AND (j.end_date IS NULL OR j.end_date > CURRENT_DATE)

    UNION ALL

    -- CONTRATO SALIENTE TOMANDO EL ÚLTIMO PUESTO
    SELECT
        bc.*, j.id AS job_id, j.name AS job_name, j.security_job_id, j.department_id,
        j.hierarchical_level_id, j.start_date, j.end_date, j.is_uo_manager
    FROM base_contract_view bc
    LEFT JOIN LATERAL (
        SELECT * FROM hr_job
        WHERE hr_job.contract_id = bc.contract_id
        ORDER BY hr_job.end_date DESC NULLS LAST, hr_job.id DESC
        LIMIT 1
    ) j ON TRUE
    WHERE bc.contract_legajo_state = 'outgoing_commission'
) AS main_query
LEFT JOIN onsc_legajo_job_hierarchy AS jh ON main_query.job_id = jh.job_id
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
