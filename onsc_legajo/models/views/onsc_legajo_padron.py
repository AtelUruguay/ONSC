# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api
from odoo.osv import expression
from odoo.tools import func


class ONSCLegajoPadron(models.Model):
    _name = "onsc.legajo.padron"
    _description = "Legajo - Padrón"
    _order = "legajo_id"

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
    #         args = self._get_domain(args)
    #     return super(ONSCLegajoPadron, self.with_context(avoid_recursion=True))._search(
    #         args,
    #         offset=offset,
    #         limit=limit,
    #         order=order,
    #         count=count,
    #         access_rights_uid=access_rights_uid
    #     )

    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     if self._context.get('is_from_menu') and not self._context.get('avoid_recursion', False):
    #         domain = self._get_domain(domain)
    #     result = super(ONSCLegajoPadron, self.with_context(avoid_recursion=True)).read_group(
    #         domain,
    #         fields,
    #         groupby,
    #         offset=offset,
    #         limit=limit,
    #         orderby=orderby,
    #         lazy=lazy
    #     )
    #     for res in result:
    #         count_key, count_key_value = next(iter(res.items()))
    #         group_key_str = count_key.split('_count')[0]
    #         group_key = res.get(group_key_str)
    #         if not group_key:
    #             res[group_key_str] = (0, func.lazy(
    #                 lambda: self.fields_get().get(group_key_str).get('string') or 'Nivel'))
    #     return result

    # def _is_group_responsable_uo_security(self):
    #     return self.user_has_groups('onsc_legajo.group_legajo_hr_responsable_uo')

    # def _get_domain(self, args):
    #     is_consult_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')
    #     is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')
    #     is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')
    #     inciso_id = self._context.get('inciso_id', False)
    #     operating_unit_id = self._context.get('operating_unit_id', False)
    #     is_any_group = is_consult_security or is_inciso_security or is_ue_security
    #     is_any_hierarchy = inciso_id or operating_unit_id
    #     if not is_any_group or not is_any_hierarchy:
    #         return expression.AND([[(True,'=',False)], args])
    #     contract_ids = self._get_contract_ids(inciso_id, operating_unit_id)
    #     args = expression.AND([[
    #         ('contract_id', 'in', contract_ids),
    #         # ('contract_id','=',37)
    #     ], args])
    #     return args

    # def _get_contract_ids(self, inciso_id=False, operating_unit_id=False):
    #     available_contracts = self._get_hierarchy_available_contract(
    #         inciso_id=inciso_id,
    #         operating_unit_id=operating_unit_id,
    #         date=self._context.get('date', fields.Date.today()),
    #     )
    #     return available_contracts.ids

    # def _get_hierarchy_available_contract(self, inciso_id=False, operating_unit_id=False, date=False):
    #     available_contracts = self.env['hr.contract']
    #     base_employee_domain = [('id', '!=', self.env.user.employee_id.id)]
    #     base_employee_domain = []
    #     employee_domain = []
    #     if date:
    #         employee_domain = expression.AND([[
    #             ('date_start', '<=', date),
    #             '|',
    #             ('date_end', '=', False),
    #             ('date_end', '>=', date)],
    #             employee_domain])
    #     if operating_unit_id:
    #         available_contracts = self._get_available_contracts(
    #             base_employee_domain,
    #             employee_domain,
    #             operating_unit_id,
    #             'operating_unit_id'
    #         )
    #     else:
    #         available_contracts = self._get_available_contracts(
    #             base_employee_domain,
    #             employee_domain,
    #             inciso_id,
    #             'inciso_id',
    #         )
    #     return available_contracts

    # def _get_available_contracts(
    #         self,
    #         base_employee_domain,
    #         employee_domain,
    #         security_hierarchy_value,
    #         security_hierarchy_level,
    # ):
    #     base_args = employee_domain
    #     # LEGAJOS VIGENTES
    #     base_args = expression.AND([[
    #         (security_hierarchy_level, '=', security_hierarchy_value)],
    #         base_args])
    #     available_contracts = self.env['hr.contract'].search(base_args)

    #     return available_contracts

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoPadron, self).fields_get(allfields, attributes)
        hide = ['end_date', 'employee_id', 'job_id', 'type', 'active_job_qty', 'job_end_date', 'token', 'report_user_id', 'create_uid', 'write_uid', 'create_date', 'write_date']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    # CONTRACT INFO
    token = fields.Char(string='Token', index=True)
    report_user_id = fields.Integer(string='Usuario que dió origen al reporte', index=True)

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
                                             )
    job_id = fields.Many2one('hr.job', string="Puesto")
    job_name = fields.Char(string='Nombre del puesto')
    security_job_id = fields.Many2one('onsc.legajo.security.job', string="Seguridad de puesto")
    department_id = fields.Many2one('hr.department', string="UO")
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel de UO")
    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?')


    job_start_date = fields.Date(string='Fecha desde')
    job_end_date = fields.Date(string='Fecha hasta')
    # CONTRACT COMPUTED INFO - HISTORICAL DATA
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')

    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    commission_regime_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen comisión')
    inciso_origin_id = fields.Many2one('onsc.catalog.inciso', string='Inciso origen')
    operating_unit_origin_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora origen",

    )
    inciso_dest_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso destino',

    )
    operating_unit_dest_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora destino",

    )
    date_start = fields.Date(string=u'Fecha de alta')
    date_end = fields.Date(string=u'Fecha de baja')
    date_end_commission = fields.Date(string=u'Fecha hasta de la comisión')
    reason_description = fields.Char(string='Motivo de alta')
    reason_deregistration = fields.Char(string='Motivo de baja')
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string="Causal de egreso")
    extinction_commission_id = fields.Many2one("onsc.legajo.reason.extinction.commission", string="Motivo de extinción de la comisión")
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones')

    # JOB COMPUTED INFO
    # organigram_joker = fields.Many2one('hr.department', string='Organigrama')
    level_0 = fields.Many2one('hr.department', string='Nivel 0')
    level_1 = fields.Many2one('hr.department', string='Nivel 1')
    level_2 = fields.Many2one('hr.department', string='Nivel 2')
    level_3 = fields.Many2one('hr.department', string='Nivel 3')
    level_4 = fields.Many2one('hr.department', string='Nivel 4')
    level_5 = fields.Many2one('hr.department', string='Nivel 5')

    # def _compute_contract_info(self):
    #     LegajoUtils = self.env['onsc.legajo.utils']
    #     contract_ids = self.mapped('contract_id.id')
    #     _date = self._context.get('date', fields.Date.today())
    #     if isinstance(_date, str):  # Si viene como string, lo convertimos
    #         _date = fields.Date.from_string(_date)

    #     last_states = LegajoUtils._get_last_states_dict(contract_ids, _date)
    #     current_jobs = LegajoUtils._get_contracts_jobs_dict(contract_ids, _date)

    #     for record in self:
    #         record.contract_legajo_state = last_states.get(record.id, False)
    #         job_dict = current_jobs.get(record.id, {})
    #         record.job_id = job_dict.get('job_id', False)
    #         record.job_name = job_dict.get('job_name', False)
    #         record.security_job_id = job_dict.get('security_job_id', False)
    #         record.department_id = job_dict.get('department_id', False)
    #         record.hierarchical_level_id = job_dict.get('hierarchical_level_id', False)
    #         record.is_uo_manager = job_dict.get('is_uo_manager', False)
    #         record.job_start_date = job_dict.get('job_start_date', False)
    #         record.job_end_date = job_dict.get('job_end_date', False)
    #         record.level_0 = job_dict.get('level_0', False)
    #         record.level_1 = job_dict.get('level_1', False)
    #         record.level_2 = job_dict.get('level_2', False)
    #         record.level_3 = job_dict.get('level_3', False)
    #         record.level_4 = job_dict.get('level_4', False)
    #         record.level_5 = job_dict.get('level_5', False)

    #         # Obtener datos históricos o actuales del contrato
    #         contract_data = LegajoUtils._get_historical_contract_data(record.contract_id, _date)
    #         # Asignar valores
    #         for field, value in contract_data.items():
    #             setattr(record, field, value)

#     def init(self):
#         tools.drop_view_if_exists(self.env.cr, self._table)
#         self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS (
# WITH base_contract_view AS (
#     SELECT
#         contract.id AS id,
#         contract.legajo_id,
#         contract.id AS contract_id,
#         contract.legajo_state AS legajo_state,
#         contract.inciso_id,
#         contract.operating_unit_id,
#         contract.employee_id,
#         'active' AS type,
#         contract.nro_doc,
#         contract.public_admin_entry_date,
#         contract.first_operating_unit_entry_date
#     FROM hr_contract contract
#     WHERE contract.legajo_id IS NOT NULL
# )
# SELECT
#     bc.*
# FROM base_contract_view bc
# )''' % (self._table,))

    # def _search_descriptor1_id(self, operator, value):
    #     valid_contracts = self.env['hr.contract'].search([('descriptor1_id', operator, value)])
    #     return [('contract_id', 'in', valid_contracts.ids)]
