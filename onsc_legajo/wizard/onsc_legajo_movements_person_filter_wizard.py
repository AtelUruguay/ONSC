# -*- coding: utf-8 -*-
import json
import logging
import uuid

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ONSCLegajoPadronEstructureFilterWizard(models.TransientModel):
    _name = 'onsc.legajo.person.movements.filter.wizard'
    _inherit = 'onsc.legajo.abstract.opaddmodify.security'
    _description = 'Wizard para filtrar movimientos para una persona'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Unidad Ejecutora'
    )
    date_from = fields.Date(string='Fecha de inicio', required=True)
    date_to = fields.Date(string='Fecha de fin', required=True)
    employee_id = fields.Many2one("hr.employee", string="Funcionario")
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute="_compute_employee_domain")
    contract_id = fields.Many2one('hr.contract', 'Contrato', copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute="_compute_contract_domain")
    show_contract = fields.Boolean(string="Mostrar contratos?", compute="_compute_contract_domain")

    @api.depends('date_from', 'date_to', 'inciso_id', 'operating_unit_id')
    def _compute_employee_domain(self):
        for rec in self:
            contracts = self._get_contracts()
            employees = contracts.mapped('employee_id')
            if employees:
                rec.employee_id_domain = json.dumps([('id', 'in', employees.ids)])
            else:
                rec.employee_id_domain = json.dumps([('id', '=', False)])
    @api.depends('employee_id')
    def _compute_contract_domain(self):
        for rec in self:
            contracts = self._get_contracts()
            if contracts and rec.employee_id:
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
                if len(contracts) == 1:
                    rec.show_contract = False
                    rec.contract_id = contracts.id
                else:
                    rec.show_contract = True
                    rec.contract_id = False
            else:
                rec.contract_id_domain = json.dumps([('id', '=', False)])
                rec.show_contract = False

    def _get_contracts(self):
        args = [('inciso_id', '=', self.inciso_id.id),
                ('date_start', '>=', fields.Date.to_string(self.date_from)), '|',
                ('date_end', '<=', fields.Date.to_string(self.date_to)), ('date_end', '=', False)]
        if self.employee_id:
            args = expression.AND([[('employee_id', '=', self.employee_id.id)], args])

        if self.operating_unit_id:
            args = expression.AND([[('operating_unit_id', '=', self.operating_unit_id.id)], args])

        return self.env['hr.contract'].suspend_security().search(args)

    @api.onchange('inciso_id', 'operating_unit_id')
    def _onchange_inciso_operating_unit(self):
        self.date_from = False
        self.date_to = False
        self.employee_id = False
        self.contract_id = False

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            self.date_to = False
            return cv_warning(_("La fecha hasta no puede ser menor a la fecha desde."))
        if self.date_from and self.date_from > fields.Date.today():
            self.date_from = False
            return cv_warning(_("La fecha desde no puede ser mayor a la fecha actual."))
        if self.date_to and self.date_to > fields.Date.today():
            self.date_to = False
            return cv_warning(_("La fecha hasta no puede ser mayor a la fecha actual."))
        self.employee_id = False
        self.contract_id = False


    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_person_movements_consult')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_person_movements_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_person_movements_ue')

    def action_show(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_person_movements_action').sudo().read()[0]
        original_context = safe_eval(action.get('context', '{}'))
        _token = str(uuid.uuid4())
        new_context = {
            **original_context,
            **self.env.context,
            'operating_unit_id': self.operating_unit_id.id,
            'inciso_id': self.inciso_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_id': self.employee_id.id,
            'contract_id': self.contract_id.id,
            'token': _token,
        }
        self._set_info(
            _token,
            self.date_from,
            self.date_to,
            self.contract_id)
        action['domain'] = [('token', '=', _token)]
        action['context'] = new_context
        return action


    def _get_base_sql(self, date_from, date_to, contract):
        _sql1 = """
    WITH primer_estado AS (
      SELECT contract_id, from_state,to_state
      FROM hr_contract contract
      LEFT JOIN hr_contract_state_transaction_history history ON contract.id = history.contract_id
      ORDER BY transaction_date ASC
      LIMIT 1
    )
    SELECT
        history.id AS id,
        history.id AS history_id,
        contract.id AS contract_id,
        contract.legajo_id,
        contract.inciso_id,
        contract.operating_unit_id,
        contract.employee_id,
        contract.date_start,
    --    'active' AS type,
        contract.nro_doc,
        contract.public_admin_entry_date,
        contract.first_operating_unit_entry_date,
        --
        contract.descriptor1_id,
        contract.descriptor2_id,
        contract.descriptor3_id,
        contract.descriptor4_id,
        contract.regime_id,
        contract.commission_regime_id,
        contract.inciso_origin_id,
        contract.operating_unit_origin_id,
        contract.inciso_dest_id,
        contract.operating_unit_dest_id,
        contract.eff_date,
        contract.date_start,
        contract.date_end,
        contract.date_end_commission,
        contract.reason_description,
        contract.reason_deregistration,
        contract.income_mechanism_id,
        contract.causes_discharge_id,
        contract.extinction_commission_id,
        history.to_state AS contract_legajo_state,
        history.transaction_date::DATE,
        CASE
            WHEN history.to_state in ('outgoing_commission','incoming_commission') THEN  contract.eff_date
            ELSE null
        END AS date_start_commission,
        CASE
            WHEN history.to_state = 'active' and history.from_state is null and contract.cs_contract_id is null  THEN 'alta'
            WHEN history.to_state = 'baja' and contract.cs_contract_id is null  THEN 'baja'
            WHEN history.to_state = 'incoming_commission' and contract.cs_contract_id is null  THEN 'comision_alta'
            WHEN (history.to_state = 'outgoing_commission' and contract.cs_contract_id is null) or (history.to_state = 'outgoing_commission' and history.from_state = 'active') THEN 'comision_alta'
            WHEN history.to_state = 'baja' and history.from_state = 'incoming_commission' and contract.extinction_commission_id is not null THEN 'comision_baja'
            WHEN history.to_state = 'active' and history.from_state = 'incoming_commission' THEN 'comision_baja'
            WHEN history.to_state = 'baja'
              AND history.from_state = 'outgoing_commission'
              AND NOT EXISTS (
                SELECT 1 FROM primer_estado pe
                WHERE pe.contract_id = history.contract_id and to_state = 'active' and from_state is null
              )
            THEN 'comision_baja'
            ELSE null
        END AS move_type
       
    FROM hr_contract contract
    LEFT JOIN hr_contract_state_transaction_history history ON contract.id = history.contract_id
    WHERE
        contract.id = %s AND
        history.transaction_date::DATE BETWEEN '%s' AND '%s' 
    """ % (contract.id, date_from, date_to)

        return _sql1


    def _get_record_job_vals(self, record, job_dict):
        return {
            'department_id': job_dict.get('department_id', False),
            'hierarchical_level_id': job_dict.get('hierarchical_level_id', False),
            'is_uo_manager': job_dict.get('is_uo_manager', False),
        }


    def _set_info(self, token, date_from, date_to, contract_id):
        LegajoUtils = self.env['onsc.legajo.utils']
        is_consult_security = self.user_has_groups('onsc_legajo.group_legajo_report_person_movements_consult')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_person_movements_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_person_movements_ue')

        is_any_group = is_consult_security or is_inciso_security or is_ue_security
        # is_any_hierarchy = inciso or operating_unit
        # if not is_any_group or not is_any_hierarchy:
        #     return self.search([('id', '=', 0)])
        _sql = self._get_base_sql(date_from, date_to, contract_id)
        self.env.cr.execute(
            '''DELETE FROM onsc_legajo_person_movements WHERE report_user_id = %s''' % (self.env.user.id,))
        self.env.cr.execute(_sql)
        contract_records = self.env.cr.dictfetchall()
        bulked_vals = []
        user_id = self.env.user.id
        for result in contract_records:
            contract_id = result['contract_id']
            current_jobs = LegajoUtils._get_contracts_jobs_dict([contract_id],
                                                                result.get('transaction_date', fields.Date.today()))
            job_dict = current_jobs.get(contract_id, {})
            new_record = self._get_record_job_vals(result, job_dict)
            for field, value in result.items():
                new_record[field] = value
            contract_data = LegajoUtils._get_historical_contract_data(result, result.get('transaction_date',
                                                                                         fields.Date.today()))
            for key, value in contract_data.items():
                new_record[key] = value
            new_record['report_user_id'] = user_id
            new_record['token'] = token
            new_record.pop('id')
            new_record.pop('eff_date')

            bulked_vals.append(new_record)
        result = self.env['onsc.legajo.person.movements'].sudo().create(bulked_vals)
        return result
