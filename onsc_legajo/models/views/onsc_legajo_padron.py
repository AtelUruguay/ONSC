# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api
from odoo.osv import expression
from odoo.tools import func


class ONSCLegajoPadron(models.Model):
    _name = "onsc.legajo.padron"
    _description = "Legajo - Padrón"
    _auto = False
    _order = "legajo_id"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            args = self._get_domain(args)
        return super(ONSCLegajoPadron, self.with_context(avoid_recursion=True))._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid
        )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
            domain = self._get_domain(domain)
        result = super(ONSCLegajoPadron, self.with_context(avoid_recursion=True)).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
        )
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
        is_consult_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')
        inciso_id = self._context.get('inciso_id', False)
        operating_unit_id = self._context.get('operating_unit_id', False)
        is_any_group = is_consult_security or is_inciso_security or is_ue_security
        is_any_hierarchy = inciso_id or operating_unit_id
        if not is_any_group or not is_any_hierarchy:
            return expression.AND([[(True,'=',False)], args])
        contract_ids = self._get_contract_ids(inciso_id, operating_unit_id)
        args = expression.AND([[
            ('contract_id', 'in', contract_ids),
            # ('contract_id','=',37)
        ], args])
        return args

    def _get_contract_ids(self, inciso_id=False, operating_unit_id=False):
        available_contracts = self._get_hierarchy_available_contract(
            inciso_id=inciso_id,
            operating_unit_id=operating_unit_id,
            date=self._context.get('date', fields.Date.today()),
        )
        return available_contracts.ids

    def _get_hierarchy_available_contract(self, inciso_id=False, operating_unit_id=False, date=False):
        available_contracts = self.env['hr.contract']
        base_employee_domain = [('id', '!=', self.env.user.employee_id.id)]
        base_employee_domain = []
        employee_domain = []
        if date:
            employee_domain = expression.AND([[
                ('date_start', '<=', date),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', date)],
                employee_domain])
        if operating_unit_id:
            available_contracts = self._get_available_contracts(
                base_employee_domain,
                employee_domain,
                operating_unit_id,
                'operating_unit_id'
            )
        else:
            available_contracts = self._get_available_contracts(
                base_employee_domain,
                employee_domain,
                inciso_id,
                'inciso_id',
            )
        return available_contracts

    def _get_available_contracts(
            self,
            base_employee_domain,
            employee_domain,
            security_hierarchy_value,
            security_hierarchy_level,
    ):
        base_args = employee_domain
        # LEGAJOS VIGENTES
        base_args = expression.AND([[
            (security_hierarchy_level, '=', security_hierarchy_value)],
            base_args])
        available_contracts = self.env['hr.contract'].search(base_args)

        return available_contracts

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoPadron, self).fields_get(allfields, attributes)
        hide = ['end_date', 'employee_id', 'job_id', 'type', 'active_job_qty', 'start_date']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    # CONTRACT INFO
    legajo_id = fields.Many2one('onsc.legajo', string="Funcionario")
    contract_id = fields.Many2one('hr.contract', string="Contrato")
    legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    employee_id = fields.Many2one('hr.employee', string="Funcionario")
    type = fields.Selection(string='Tipo', selection=[('active', 'Activo'), ('egresed', 'Egresado')])
    nro_doc = fields.Char(u'Número de documento')
    public_admin_entry_date = fields.Date(string=u'Fecha de ingreso AP')
    first_operating_unit_entry_date = fields.Date(string=u'Fecha de ingreso UE')

    # CONTRACT COMPUTED INFO
    contract_legajo_state = fields.Selection([
        ('active', 'Activo'),
        ('baja', 'Baja'),
        ('reserved', 'Reservado'),
        ('outgoing_commission', 'Comisión saliente'),
        ('incoming_commission', 'Comisión entrante')], string='Estado del contrato',
                                             compute='_compute_contract_info')
    job_id = fields.Many2one('hr.job', string="Puesto", compute='_compute_contract_info')
    job_name = fields.Char(string='Nombre del puesto', compute='_compute_contract_info')
    security_job_id = fields.Many2one('onsc.legajo.security.job', string="Seguridad de puesto", compute='_compute_contract_info')
    department_id = fields.Many2one('hr.department', string="UO", compute='_compute_contract_info')
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel de UO", compute='_compute_contract_info')
    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?', compute='_compute_contract_info')


    job_start_date = fields.Date(string='Fecha desde (Puesto)', compute='_compute_contract_info')
    job_end_date = fields.Date(string='Fecha hasta (Puesto)', compute='_compute_contract_info')
    # CONTRACT COMPUTED INFO - HISTORICAL DATA
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1', compute='_compute_contract_info', search='_search_descriptor1_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2', compute='_compute_contract_info')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3', compute='_compute_contract_info')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4', compute='_compute_contract_info')

    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', compute='_compute_contract_info')
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión', compute='_compute_contract_info')
    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen', compute='_compute_contract_info')
    operating_unit_origin_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora origen",
        compute='_compute_contract_info'
    )
    inciso_dest_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso destino',
        compute='_compute_contract_info'
    )
    operating_unit_dest_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora destino",
        compute='_compute_contract_info'
    )
    date_start = fields.Date(string=u'Fecha de alta', compute='_compute_contract_info')
    date_end = fields.Date(string=u'Fecha de baja', compute='_compute_contract_info')
    date_end_commission = fields.Date(string=u'Fecha hasta de la comisión', compute='_compute_contract_info')
    reason_description = fields.Char(string='Motivo de alta', compute='_compute_contract_info')
    reason_deregistration = fields.Char(string='Motivo de baja', compute='_compute_contract_info')
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso', compute='_compute_contract_info')
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string="Causal de egreso", compute='_compute_contract_info')
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission", string="Motivo de extinción de la comisión", compute='_compute_contract_info')
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones', compute='_compute_contract_info')

    # JOB COMPUTED INFO
    # organigram_joker = fields.Many2one('hr.department', string='Organigrama')
    level_0 = fields.Many2one('hr.department', string='Nivel 0', compute='_compute_contract_info')
    level_1 = fields.Many2one('hr.department', string='Nivel 1', compute='_compute_contract_info')
    level_2 = fields.Many2one('hr.department', string='Nivel 2', compute='_compute_contract_info')
    level_3 = fields.Many2one('hr.department', string='Nivel 3', compute='_compute_contract_info')
    level_4 = fields.Many2one('hr.department', string='Nivel 4', compute='_compute_contract_info')
    level_5 = fields.Many2one('hr.department', string='Nivel 5', compute='_compute_contract_info')


    def _get_last_states_dict(self, contract_ids, date):
        """
        Retrieve the last known states of contracts up to a specified date.

        This method queries the database to fetch the most recent state transitions
        for a given set of contract IDs, up to and including the specified date.
        It returns a dictionary mapping each contract ID to its last known state.

        Args:
            contract_ids (list[int]): A list of contract IDs to query.
            date (str): The cutoff date (in 'YYYY-MM-DD' format) for fetching the last states.

        Returns:
            dict: A dictionary where the keys are contract IDs and the values are the
                  corresponding last known states (as strings) up to the specified date.

        Notes:
            - The query uses a Common Table Expression (CTE) to identify the most recent
              transaction for each contract ID.
            - The `transaction_date` column is cast to a date to ensure proper comparison.
        """
        self.env.cr.execute('''
            WITH last_transaction AS (
                SELECT DISTINCT ON (contract_id) *
                FROM hr_contract_state_transaction_history
                WHERE contract_id IN %s AND transaction_date::DATE <= %s
                ORDER BY contract_id, transaction_date DESC
            )
            SELECT contract_id, to_state AS legajo_state, transaction_date
            FROM last_transaction
        ''', (tuple(contract_ids), date))
        result = self.env.cr.dictfetchall()
        return {rec['contract_id']: rec['legajo_state'] for rec in result}

    def _get_contracts_jobs_dict(self, contract_ids, date):
        """
        Retrieves a dictionary mapping contract IDs to the first valid job ID
        based on the provided date.

        This method queries the `hr_job` table to find jobs associated with the
        given contract IDs that are valid for the specified date. A job is
        considered valid if its start date is on or before the target date and
        its end date is either null or on/after the target date. The first valid
        job for each contract (ordered by start date) is selected.

        Args:
            contract_ids (list): A list of contract IDs to filter jobs.
            date (str): The target date (in 'YYYY-MM-DD' format) to check job validity.

        Returns:
            dict: A dictionary where the keys are contract IDs and the values are
                  the corresponding job IDs of the first valid job for each contract.
        """

        self.env.cr.execute('''
            SELECT DISTINCT ON (j.contract_id)
                j.contract_id,
                j.id AS job_id,
                j.name AS job_name,
                j.security_job_id,
                j.department_id,
                j.hierarchical_level_id,
                j.is_uo_manager,
                j.start_date,
                j.end_date,
                jh.*
            FROM hr_job j LEFT JOIN onsc_legajo_job_hierarchy AS jh ON j.id = jh.job_id
            WHERE j.contract_id IN %s
                AND j.start_date <= %s::DATE  -- La fecha de inicio debe ser anterior o igual al target_date
                AND (j.end_date IS NULL OR j.end_date >= %s::DATE)  -- Si end_date es NULL o mayor/igual, sigue vigente
            ORDER BY j.contract_id, j.start_date ASC  -- Para tomar el primer puesto válido''', (tuple(contract_ids), date, date))
        result = self.env.cr.dictfetchall()
        return {rec['contract_id']: {'job_id': rec['job_id'],
                                     'job_name':rec['job_name'],
                                     'security_job_id':rec['security_job_id'],
                                     'department_id':rec['department_id'],
                                     'hierarchical_level_id':rec['hierarchical_level_id'],
                                     'is_uo_manager':rec['is_uo_manager'],
                                     'job_start_date':rec['start_date'],
                                     'job_end_date':rec['end_date'],
                                     'level_0': rec['level_0'],
                                     'level_1': rec['level_1'],
                                     'level_2': rec['level_2'],
                                     'level_3': rec['level_3'],
                                     'level_4': rec['level_4'],
                                     'level_5': rec['level_5'],
                                    } for rec in result}

    def _compute_contract_info(self):
        contract_ids = self.mapped('contract_id.id')
        _date = self._context.get('date', fields.Date.today())
        if isinstance(_date, str):  # Si viene como string, lo convertimos
            _date = fields.Date.from_string(_date)

        last_states = self._get_last_states_dict(contract_ids, _date)
        current_jobs = self._get_contracts_jobs_dict(contract_ids, _date)

        for record in self:
            record.contract_legajo_state = last_states.get(record.id, False)
            job_dict = current_jobs.get(record.id, {})
            record.job_id = job_dict.get('job_id', False)
            record.job_name = job_dict.get('job_name', False)
            record.security_job_id = job_dict.get('security_job_id', False)
            record.department_id = job_dict.get('department_id', False)
            record.hierarchical_level_id = job_dict.get('hierarchical_level_id', False)
            record.is_uo_manager = job_dict.get('is_uo_manager', False)
            record.job_start_date = job_dict.get('job_start_date', False)
            record.job_end_date = job_dict.get('job_end_date', False)
            record.level_0 = job_dict.get('level_0', False)
            record.level_1 = job_dict.get('level_1', False)
            record.level_2 = job_dict.get('level_2', False)
            record.level_3 = job_dict.get('level_3', False)
            record.level_4 = job_dict.get('level_4', False)
            record.level_5 = job_dict.get('level_5', False)

            # Obtener datos históricos o actuales del contrato
            contract_data = self._get_historical_contract_data(record.contract_id, _date)
            # Asignar valores
            for field, value in contract_data.items():
                setattr(record, field, value)

    def _get_historical_contract_data(self, contract, _date):
        contract = contract.sudo()
        if contract.eff_date <= _date:
            return {
                'descriptor1_id': contract.descriptor1_id.id,
                'descriptor2_id': contract.descriptor2_id.id,
                'descriptor3_id': contract.descriptor3_id.id,
                'descriptor4_id': contract.descriptor4_id.id,
                'regime_id': contract.regime_id.id,
                'commission_regime_id': contract.commission_regime_id.id,
                'inciso_origin_id': contract.inciso_origin_id.id,
                'operating_unit_origin_id': contract.operating_unit_origin_id.id,
                'inciso_dest_id': contract.inciso_dest_id.id,
                'operating_unit_dest_id': contract.operating_unit_dest_id.id,
                'date_start': contract.date_start,
                'date_end': contract.date_end,
                'date_end_commission': contract.date_end_commission,
                'reason_description': contract.reason_description,
                'reason_deregistration': contract.reason_deregistration,
                'income_mechanism_id': contract.income_mechanism_id.id,
                'causes_discharge_id': contract.causes_discharge_id.id,
                'extinction_commission_id': contract.extinction_commission_id.id,
                'legajo_state_id': contract.legajo_state_id.id,
            }
        else:
            history_data = contract.with_context(as_of_date=_date).sudo().read_history(as_of_date=_date)
            return {
                'descriptor1_id': history_data.get('descriptor1_id', contract.descriptor1_id.id),
                'descriptor2_id': history_data.get('descriptor2_id', contract.descriptor2_id.id),
                'descriptor3_id': history_data.get('descriptor3_id', contract.descriptor3_id.id),
                'descriptor4_id': history_data.get('descriptor4_id', contract.descriptor4_id.id),
                'regime_id': history_data.get('regime_id', contract.regime_id.id),
                'commission_regime_id': history_data.get('commission_regime_id', contract.commission_regime_id.id),
                'inciso_origin_id': history_data.get('inciso_origin_id', contract.inciso_origin_id.id),
                'operating_unit_origin_id': history_data.get('operating_unit_origin_id', contract.operating_unit_origin_id.id),
                'inciso_dest_id': history_data.get('inciso_dest_id', contract.inciso_dest_id.id),
                'operating_unit_dest_id': history_data.get('operating_unit_dest_id', contract.operating_unit_dest_id.id),
                'date_start': history_data.get('date_start', contract.date_start),
                'date_end': history_data.get('date_end', contract.date_end),
                'date_end_commission': history_data.get('date_end_commission', contract.date_end_commission),
                'reason_description': history_data.get('reason_description', contract.reason_description),
                'reason_deregistration': history_data.get('reason_deregistration', contract.reason_deregistration),
                'income_mechanism_id': history_data.get('income_mechanism_id', contract.income_mechanism_id.id),
                'causes_discharge_id': history_data.get('causes_discharge_id', contract.causes_discharge_id.id),
                'extinction_commission_id': history_data.get('extinction_commission_id', contract.extinction_commission_id.id),
                'legajo_state_id': history_data.get('legajo_state_id', contract.legajo_state_id.id),
            }

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
WITH base_contract_view AS (
    SELECT
        contract.id AS id,
        contract.legajo_id,
        contract.id AS contract_id,
        contract.legajo_state AS legajo_state,
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
        --contract.descriptor4_id,
        contract.nro_doc,
        contract.public_admin_entry_date,
        contract.first_operating_unit_entry_date,
        contract.date_end,
        contract.date_end_commission
    FROM hr_contract contract
    WHERE contract.legajo_id IS NOT NULL
)
SELECT
    bc.*
FROM base_contract_view bc
)''' % (self._table,))

    def _search_descriptor1_id(self, operator, value):
        valid_contracts = self.env['hr.contract'].search([('descriptor1_id', operator, value)])
        return [('contract_id', 'in', valid_contracts.ids)]
