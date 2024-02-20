# -*- coding: utf-8 -*-
from odoo.addons.onsc_base.onsc_useful_tools import profiler

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
            is_legajo_id_in_base_args = False
            for arg in args:
                if (isinstance(arg, tuple) or isinstance(arg, list)) and len(arg) and arg[0] == 'legajo_id':
                    is_legajo_id_in_base_args = True
            if not is_legajo_id_in_base_args:
                args = self._get_domain(args)
        return super(ONSCLegajoDepartment, self.with_context(avoid_recursion = True))._search(args, offset=offset, limit=limit, order=order,
                                                         count=count,
                                                         access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            is_legajo_id_in_base_args = False
            for arg in domain:
                if (isinstance(arg, tuple) or isinstance(arg, list)) and len(arg) and arg[0] == 'legajo_id':
                    is_legajo_id_in_base_args = True
            if not is_legajo_id_in_base_args:
                domain = self._get_domain(domain)
        return super(ONSCLegajoDepartment, self.with_context(avoid_recursion = True)).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def _is_group_responsable_uo_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo')

    def _get_domain(self, args):
        is_config_security = self.user_has_groups(
            'onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_configurador_legajo')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_hr_ue')

        if is_config_security:
            legajo_ids = self._get_legajo_ids()
            args = expression.AND([[
                ('legajo_id', 'in', legajo_ids),
            ], args])
        elif is_inciso_security:
            legajo_ids = self._get_legajo_ids()
            contract = self.env.user.employee_id.job_id.contract_id
            args = expression.AND([[
                ('legajo_id', 'in', legajo_ids),
                ('inciso_id', '=', contract.inciso_id.id)
            ], args])
        elif is_ue_security:
            legajo_ids = self._get_legajo_ids()
            contract = self.env.user.employee_id.job_id.contract_id
            args = expression.AND([[
                ('legajo_id', 'in', legajo_ids),
                ('operating_unit_id', '=', contract.operating_unit_id.id)
            ], args])
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            args = expression.AND([[
                ('department_id', 'in', department_ids),
                ('type', '=', 'active'),
            ], args])
        return args

    def _get_legajo_ids(self):
        available_contracts = self.env['onsc.legajo']._get_user_available_contract()
        sql_query = """SELECT DISTINCT legajo_id FROM hr_contract WHERE id IN %s AND employee_id IS NOT NULL"""
        self.env.cr.execute(sql_query, [tuple(available_contracts.ids)])
        results = self.env.cr.fetchall()
        return [item[0] for item in results]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoDepartment, self).fields_get(allfields, attributes)
        hide = ['is_job_open', 'end_date', 'employee_id', 'job_id']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

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
    type = fields.Selection(
        string='Tipo',
        selection=[('active', 'Activo'),
                   ('egresed', 'Egresado')],
        required=False)

    active_job_qty = fields.Integer(string='Cantidad de puestos activos (por Legajo)')

    # last_job_id = fields.Many2one('hr.job', string="Puesto")
    # last_inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    # last_operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")

    is_job_open = fields.Boolean(string='¿Puesto vigente?',
                                 compute='_compute_is_job_open',
                                 search='_search_is_job_open')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
SELECT
row_number() OVER(ORDER BY legajo_id, contract_id, type, job_id) AS id, *
FROM
(SELECT
    contract.legajo_id AS legajo_id,
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
    'active' AS type,
    (SELECT COUNT(id) FROM hr_job WHERE active = True AND (end_date IS NULL OR end_date > CURRENT_DATE) AND legajo_id = legajo.id) AS active_job_qty
    --(SELECT id FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC, id DESC limit 1) AS last_job_id,
    --(SELECT inciso_id FROM hr_contract WHERE legajo_id = legajo.id ORDER BY date_start DESC, id DESC limit 1) AS last_inciso_id,
    --(SELECT operating_unit_id FROM hr_contract WHERE legajo_id = legajo.id ORDER BY date_start DESC, id DESC limit 1) AS last_operating_unit_id    
FROM
    hr_contract contract
LEFT JOIN hr_job job ON job.contract_id = contract.id
LEFT JOIN onsc_legajo legajo ON contract.legajo_id = legajo.id
WHERE 
    contract.legajo_state <> 'baja' AND ((job.start_date <= CURRENT_DATE AND (job.end_date IS NULL OR job.end_date >= CURRENT_DATE)) OR job.id IS NULL)
UNION ALL
SELECT
    legajo.id AS legajo_id,
    NULL AS contract_id,
    legajo.legajo_state AS legajo_state,
    NULL AS contract_legajo_state,
    (SELECT id FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC limit 1) AS job_id,
    (SELECT name FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC limit 1) AS job_name,
	NULL AS security_job_id,
	(SELECT inciso_id FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC limit 1) AS inciso_id,
	(SELECT operating_unit_id FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC limit 1) AS operating_unit_id,	
    legajo.employee_id,
    (SELECT department_id FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC limit 1) AS department_id,
    NULL AS start_date,
    NULL AS end_date,
    'egresed' AS type,
    0 AS active_job_qty
    --(SELECT id FROM hr_job WHERE legajo_id = legajo.id ORDER BY start_date DESC, id DESC limit 1) AS last_job_id,
    --(SELECT inciso_id FROM hr_contract WHERE legajo_id = legajo.id ORDER BY date_start DESC, id DESC limit 1) AS last_inciso_id,
    --(SELECT operating_unit_id FROM hr_contract WHERE legajo_id = legajo.id ORDER BY date_start DESC, id DESC limit 1) AS last_operating_unit_id
FROM
    onsc_legajo legajo
WHERE legajo.legajo_state = 'egresed'
) AS main_query)''' % (self._table,))

    @profiler
    def _search_is_job_open(self, operator, value):
        _today = fields.Date.today()
        base_args = [
            ('type', '=', 'active'),
        ]
        # job_expression = ['&', ('start_date', '<=', _today), '|', ('end_date', '>=', _today), ('end_date', '=', False)]
        # nojob_expression = [('job_id', '=', False), ('contract_legajo_state', '!=', 'baja')]
        # second_expression = expression.OR([job_expression, nojob_expression])
        # base_args = expression.AND([base_args, second_expression])
        open_active_records = self.search(base_args)
        open_active_records_ids = open_active_records.ids
        sql_legajo_ids_query = """SELECT legajo_id FROM onsc_legajo_department WHERE id IN %s"""
        self.env.cr.execute(sql_legajo_ids_query, [tuple(open_active_records_ids)])
        results = self.env.cr.fetchall()

        # CANDIDATOS A INDEFINIDOS
        unicity_egresed_legajo_ids = [item[0] for item in results]
        egresed_args = [
            ('type', '=', 'egresed'),
            ('legajo_id', 'not in', unicity_egresed_legajo_ids),
            '|',
            ('legajo_state', '=', 'egresed'),  # los egresados
            '&', '&', ('legajo_state', '!=', 'egresed'), ('contract_legajo_state', '!=', 'baja'),
            ('active_job_qty', '=', 0),
            # los egresados
        ]
        egresed_records = self.search(egresed_args)

        # egresed_records = self.search([('type', '=', 'egresed')])
        # egresed_valid_records = egresed_records.filtered(lambda x: x.legajo_state == 'egresed')
        # egresed_valid_records |= egresed_records.filtered(
        #     lambda x: x.legajo_state != 'egresed' and x.contract_legajo_state != 'baja' and len(
        #         x.legajo_id.job_ids) == 0)
        #
        #
        # egresed_valid_records |= egresed_records.filtered(
        #     lambda x: x.legajo_state != 'egresed' and x.contract_legajo_state != 'baja' and len(
        #         x.contract_id.job_ids.filtered(lambda x: x.end_date is False or x.end_date >= _today)) == 0)

        # unicity_egresed_legajo_ids = open_active_records.mapped('legajo_id.id')

        unicity_egresed = self
        for egresed_record in egresed_records:
            if egresed_record.legajo_id.id not in unicity_egresed_legajo_ids:
                unicity_egresed |= egresed_record
                unicity_egresed_legajo_ids.append(egresed_record.legajo_id.id)

        if operator == '=' and value is False:
            _operator = 'not in'
        else:
            _operator = 'in'

        final_records = open_active_records
        final_records |= unicity_egresed
        return [('id', _operator, final_records.ids)]

    @api.depends('start_date', 'end_date')
    def _compute_is_job_open(self):
        _today = fields.Date.today()
        for record in self:
            record.is_job_open = record.start_date <= _today and (record.end_date is False or record.end_date >= _today)

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
