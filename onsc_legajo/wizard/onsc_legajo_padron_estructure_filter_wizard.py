# -*- coding: utf-8 -*-
import logging
import uuid

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ONSCLegajoPadronEstructureFilterWizard(models.TransientModel):
    _name = 'onsc.legajo.padron.estructure.filter.wizard'
    _inherit = 'onsc.legajo.abstract.opaddmodify.security'
    _description = 'Wizard para filtrar estructuras de padron'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Unidad Ejecutora'
    )
    date = fields.Date(string='Fecha', required=True, default=lambda self: fields.Date.today())

    @api.onchange('date')
    def _onchange_dates(self):
        if self.date and self.date > fields.Date.today():
            self.date = fields.Date.today()
            return cv_warning(_("La fecha no puede ser mayor a la fecha actual."))

    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')

    def action_show(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_padron_action').sudo().read()[0]
        # Obtener el contexto original de la acción (puede estar como cadena JSON)
        original_context = safe_eval(action.get('context', '{}'))
        _token = str(uuid.uuid4())

        self._set_info(
            _token,
            self.date,
            self.inciso_id,
            self.operating_unit_id)

        # Fusionar el contexto original con el contexto actual y los nuevos valores
        new_context = {
            **original_context,
            **self.env.context,
            'operating_unit_id': self.operating_unit_id.id,
            'inciso_id': self.inciso_id.id,
            'date': self.date,
            'token': _token,
        }
        action['context'] = new_context
        action['domain'] = [('token', '=', _token)]
        return action

    def _get_base_sql(self, token, date, inciso, operating_unit=False):
        _sql = '''
SELECT
    contract.id AS id,
    contract.legajo_id,
    contract.id AS contract_id,
    contract.legajo_state AS legajo_state,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    'active' AS type,
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
    contract.date_start,
    contract.date_end,
    contract.date_end_commission,
    contract.reason_description,
    contract.reason_deregistration,
    contract.income_mechanism_id,
    contract.causes_discharge_id,
    contract.extinction_commission_id,
    contract.legajo_state_id,
    contract.eff_date
FROM hr_contract contract
WHERE
    contract.active IS TRUE AND
    contract.legajo_id IS NOT NULL AND
    contract.inciso_id = %s AND
    contract.date_start <= '%s' AND
    (contract.date_end IS NULL OR contract.date_end >= '%s')''' % (inciso.id, date, date)
        if operating_unit:
            _sql += '''
        AND contract.operating_unit_id = %s''' % (operating_unit.id)
        return _sql

    def _get_record_job_vals(self, record, job_dict):
        return {
            'job_id': job_dict.get('job_id', False),
            'job_name': job_dict.get('job_name', False),
            'security_job_id': job_dict.get('security_job_id', False),
            'department_id': job_dict.get('department_id', False),
            'hierarchical_level_id': job_dict.get('hierarchical_level_id', False),
            'is_uo_manager': job_dict.get('is_uo_manager', False),
            'job_start_date': job_dict.get('job_start_date', False),
            'job_end_date': job_dict.get('job_end_date', False),
            'level_0': job_dict.get('level_0', False),
            'level_1': job_dict.get('level_1', False),
            'level_2': job_dict.get('level_2', False),
            'level_3': job_dict.get('level_3', False),
            'level_4': job_dict.get('level_4', False),
            'level_5': job_dict.get('level_5', False),
        }

    def _set_info(self, token, date, inciso, operating_unit=False):
        LegajoUtils = self.env['onsc.legajo.utils']
        is_consult_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')

        is_any_group = is_consult_security or is_inciso_security or is_ue_security
        is_any_hierarchy = inciso or operating_unit
        if not is_any_group or not is_any_hierarchy:
            return self.search([('id', '=', 0)])
        _sql = self._get_base_sql(token, date, inciso, operating_unit)
        self.env.cr.execute('''DELETE FROM onsc_legajo_padron WHERE report_user_id = %s''' % (self.env.user.id,))
        self.env.cr.execute(_sql)
        contract_records = self.env.cr.dictfetchall()
        contract_ids = [row['id'] for row in contract_records]
        last_states = LegajoUtils._get_last_states_dict(contract_ids, date)
        current_jobs = LegajoUtils._get_contracts_jobs_dict(contract_ids, date)
        bulked_vals = []
        user_id = self.env.user.id
        for result in contract_records:
            contract_id = result['contract_id']
            job_dict = current_jobs.get(contract_id, {})
            new_record = self._get_record_job_vals(result, job_dict)
            for field, value in result.items():
                new_record[field] = value
            contract_data = LegajoUtils._get_historical_contract_data(result, date)
            for key, value in contract_data.items():
                new_record[key] = value
            contract_id = result.get('id')
            new_record['report_user_id'] = user_id
            new_record['token'] = token
            new_record['contract_legajo_state'] = last_states.get(contract_id, False)
            new_record.pop('id')
            new_record.pop('eff_date')
            bulked_vals.append(new_record)
        result = self.env['onsc.legajo.padron'].sudo().create(bulked_vals)
        return result




class ONSCLegajoPadronEstructureMovementsFilterWizard(models.TransientModel):
    _name = 'onsc.legajo.padron.estructure.movements.filter.wizard'
    _inherit = 'onsc.legajo.abstract.opaddmodify.security'
    _description = 'Wizard para filtrar estructuras de padron'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Unidad Ejecutora'
    )
    date_from = fields.Date(string='Fecha de inicio', required=True)
    date_to = fields.Date(string='Fecha de fin', required=True)

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

    def _is_group_admin_security(self):
        if self._context.get('is_change_uo'):
            return self.user_has_groups('onsc_legajo.group_legajo_report_change_uo_consult')
        else:
            return self.user_has_groups('onsc_legajo.group_legajo_report_padron_movements_consult')

    def _is_group_inciso_security(self):
        if self._context.get('is_change_uo'):
            return self.user_has_groups('onsc_legajo.group_legajo_report_change_uo_inciso')
        else:
            return self.user_has_groups('onsc_legajo.group_legajo_report_padron_movements_inciso')

    def _is_group_ue_security(self):
        if self._context.get('is_change_uo'):
            return self.user_has_groups('onsc_legajo.group_legajo_report_change_uo_ue')
        else:
            return self.user_has_groups('onsc_legajo.group_legajo_report_padron_movements_ue')

    def action_show(self):
        original_context = safe_eval(action.get('context', '{}'))
        if self._context.get('is_change_uo'):
            action = self.env.ref('onsc_legajo.onsc_legajo_change_uo_movements_action').sudo().read()[0]
            new_context = {
                **original_context,
                **self.env.context,
                'operating_unit_id': self.operating_unit_id.id,
                'inciso_id': self.inciso_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to
            }
        else:
            action = self.env.ref('onsc_legajo.onsc_legajo_padron_movements_action').sudo().read()[0]
            _token = str(uuid.uuid4())
            new_context = {
                **original_context,
                **self.env.context,
                'operating_unit_id': self.operating_unit_id.id,
                'inciso_id': self.inciso_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'token': _token,
            }
            self._set_info(
                _token,
                self.date_from,
                self.date_to,
                self.inciso_id,
                self.operating_unit_id)
            action['domain'] = [('token', '=', _token)]
        if not self.operating_unit_id:
            new_context['search_default_group_operating_unit_id'] = True
        action['context'] = new_context
        return action

    def _get_base_sql(self, token, date_from, date_to, inciso, operating_unit=False):
        _sql1 = """
SELECT
    history.id AS id,
    history.id AS history_id,
    contract.id AS contract_id,
    contract.legajo_id,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    contract.date_start,
    'active' AS type,
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
    contract.date_start,
    contract.date_end,
    contract.date_end_commission,
    contract.reason_description,
    contract.reason_deregistration,
    contract.income_mechanism_id,
    contract.causes_discharge_id,
    contract.extinction_commission_id,
    contract.legajo_state_id,
    contract.eff_date,
    history.from_state,
    history.to_state AS contract_legajo_state,
    history.transaction_date::DATE,
    False AS is_inciso_commission
FROM hr_contract contract
LEFT JOIN hr_contract_state_transaction_history history ON contract.id = history.contract_id
LEFT JOIN hr_contract contract_parent ON contract.id = contract_parent.cs_contract_id AND contract.operating_unit_id = contract_parent.operating_unit_id AND contract_parent.active = True
WHERE
    contract.active IS TRUE AND
    contract.legajo_id IS NOT NULL AND
    contract_parent.id IS NULL AND
    history.to_state = 'active' AND
    contract.inciso_id = %s AND
    history.transaction_date::DATE BETWEEN '%s' AND '%s'
""" % (inciso.id, date_from, date_to)
        _sql2 = """
SELECT
    history.id AS id,
    history.id AS history_id,
    contract.id AS contract_id,
    contract.legajo_id,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    contract.date_start,
    'active' AS type,
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
    contract.date_start,
    contract.date_end,
    contract.date_end_commission,
    contract.reason_description,
    contract.reason_deregistration,
    contract.income_mechanism_id,
    contract.causes_discharge_id,
    contract.extinction_commission_id,
    contract.legajo_state_id,
    contract.eff_date,
    history.from_state,
    history.to_state AS contract_legajo_state,
    history.transaction_date::DATE,
    (SELECT COUNT(id) FROM hr_contract WHERE id = contract.cs_contract_id AND inciso_id = contract.inciso_id AND active = True AND legajo_state = 'outgoing_commission') > 0 AS is_inciso_commission
FROM hr_contract contract
LEFT JOIN hr_contract_state_transaction_history history ON contract.id = history.contract_id
WHERE
    contract.legajo_id IS NOT NULL AND
    history.to_state = 'incoming_commission' AND
    contract.inciso_id = %s AND
    history.transaction_date::DATE BETWEEN '%s' AND '%s'
""" % (inciso.id, date_from, date_to)
        _sql3 = """
SELECT
    history.id AS id,
    history.id AS history_id,
    contract.id AS contract_id,
    contract.legajo_id,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    contract.date_start,
    'active' AS type,
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
    contract.date_start,
    contract.date_end,
    contract.date_end_commission,
    contract.reason_description,
    contract.reason_deregistration,
    contract.income_mechanism_id,
    contract.causes_discharge_id,
    contract.extinction_commission_id,
    contract.legajo_state_id,
    contract.eff_date,
    history.from_state,
    history.to_state AS contract_legajo_state,
    history.transaction_date::DATE,
    (SELECT COUNT(id) FROM hr_contract WHERE id = contract.cs_contract_id AND inciso_id = contract.inciso_id AND active = True AND legajo_state = 'outgoing_commission') > 0 AS is_inciso_commission
FROM hr_contract contract
LEFT JOIN hr_contract_state_transaction_history history ON contract.id = history.contract_id
WHERE
    contract.legajo_id IS NOT NULL AND
    history.from_state = 'incoming_commission' AND
    history.to_state = 'baja' AND
    contract.inciso_id = %s AND
    history.transaction_date::DATE BETWEEN '%s' AND '%s'
""" % (inciso.id, date_from, date_to)
        _sql4 = """
SELECT
    history.id AS id,
    history.id AS history_id,
    contract.id AS contract_id,
    contract.legajo_id,
    contract.inciso_id,
    contract.operating_unit_id,
    contract.employee_id,
    contract.date_start,
    'active' AS type,
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
    contract.date_start,
    contract.date_end,
    contract.date_end_commission,
    contract.reason_description,
    contract.reason_deregistration,
    contract.income_mechanism_id,
    contract.causes_discharge_id,
    contract.extinction_commission_id,
    contract.legajo_state_id,
    contract.eff_date,
    history.from_state,
    history.to_state AS contract_legajo_state,
    history.transaction_date::DATE,
    False AS is_inciso_commission
FROM hr_contract contract
LEFT JOIN hr_contract_state_transaction_history history ON contract.id = history.contract_id
LEFT JOIN hr_contract contract_destination ON contract.cs_contract_id = contract_destination.id AND contract.operating_unit_id = contract_destination.operating_unit_id AND contract_destination.active = True
WHERE
    contract.legajo_id IS NOT NULL AND
    contract_destination.id IS NULL AND
    history.from_state = 'active' AND
    history.to_state = 'baja' AND
    contract.inciso_id = %s AND
    history.transaction_date::DATE BETWEEN '%s' AND '%s'
""" % (inciso.id, date_from, date_to)

        if operating_unit:
            _sql1 += '''
        AND contract.operating_unit_id = %s''' % (operating_unit.id)
            _sql2 += '''
        AND contract.operating_unit_id = %s''' % (operating_unit.id)
            _sql3 += '''
        AND contract.operating_unit_id = %s''' % (operating_unit.id)
            _sql4 += '''
        AND contract.operating_unit_id = %s''' % (operating_unit.id)

        return _sql1 + '''
UNION ALL
''' + _sql2 + '''
UNION ALL
''' + _sql3 + '''
UNION ALL
''' + _sql4

    def _get_record_job_vals(self, record, job_dict):
        return {
            'job_id': job_dict.get('job_id', False),
            'job_name': job_dict.get('job_name', False),
            'security_job_id': job_dict.get('security_job_id', False),
            'department_id': job_dict.get('department_id', False),
            'hierarchical_level_id': job_dict.get('hierarchical_level_id', False),
            'is_uo_manager': job_dict.get('is_uo_manager', False),
            'job_start_date': job_dict.get('job_start_date', False),
            'job_end_date': job_dict.get('job_end_date', False),
            'level_0': job_dict.get('level_0', False),
            'level_1': job_dict.get('level_1', False),
            'level_2': job_dict.get('level_2', False),
            'level_3': job_dict.get('level_3', False),
            'level_4': job_dict.get('level_4', False),
            'level_5': job_dict.get('level_5', False),
        }

    def _set_info(self, token, date_from, date_to, inciso, operating_unit=False):
        LegajoUtils = self.env['onsc.legajo.utils']
        is_consult_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')
        is_inciso_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')
        is_ue_security = self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')

        is_any_group = is_consult_security or is_inciso_security or is_ue_security
        is_any_hierarchy = inciso or operating_unit
        if not is_any_group or not is_any_hierarchy:
            return self.search([('id', '=', 0)])
        _sql = self._get_base_sql(token, date_from, date_to, inciso, operating_unit)
        self.env.cr.execute('''DELETE FROM onsc_legajo_padron_movements WHERE report_user_id = %s''' % (self.env.user.id,))
        self.env.cr.execute(_sql)
        contract_records = self.env.cr.dictfetchall()
        bulked_vals = []
        user_id = self.env.user.id
        for result in contract_records:
            contract_id = result['contract_id']
            current_jobs = LegajoUtils._get_contracts_jobs_dict([contract_id], result.get('transaction_date', fields.Date.today()))
            job_dict = current_jobs.get(contract_id, {})
            new_record = self._get_record_job_vals(result, job_dict)
            for field, value in result.items():
                new_record[field] = value
            contract_data = LegajoUtils._get_historical_contract_data(result, result.get('transaction_date', fields.Date.today()))
            for key, value in contract_data.items():
                new_record[key] = value
            new_record['report_user_id'] = user_id
            new_record['token'] = token
            # new_record['contract_legajo_state'] = last_states.get(contract_id, False)
            new_record.pop('id')
            new_record.pop('eff_date')
            bulked_vals.append(new_record)
        result = self.env['onsc.legajo.padron.movements'].sudo().create(bulked_vals)
        return result
