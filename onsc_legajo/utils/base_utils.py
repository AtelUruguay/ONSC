# -*- coding: utf-8 -*-

import logging

from odoo import models, _

_logger = logging.getLogger(__name__)


class ONSCLegajoUtils(models.AbstractModel):
    _name = 'onsc.legajo.utils'
    _description = 'Legajo utils ONSC'

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

    def _get_historical_contract_data(self, contract_dict, _date):
        if contract_dict.get('eff_date') > _date:
            contract_id = contract_dict.get('contract_id') or contract_dict.get('id')
            contract = self.env['hr.contract'].browse(contract_id)
            history_data = contract.with_context(as_of_date=_date).sudo().read_history(as_of_date=_date)
            return {
                'descriptor1_id': history_data.get('descriptor1_id', [contract.descriptor1_id.id])[0],
                'descriptor2_id': history_data.get('descriptor2_id', [contract.descriptor2_id.id])[0],
                'descriptor3_id': history_data.get('descriptor3_id', [contract.descriptor3_id.id])[0],
                'descriptor4_id': history_data.get('descriptor4_id', [contract.descriptor4_id.id])[0],
                'regime_id': history_data.get('regime_id', [contract.regime_id.id])[0],
                'commission_regime_id': history_data.get('commission_regime_id', [contract.commission_regime_id.id])[0],
                'inciso_origin_id': history_data.get('inciso_origin_id', [contract.inciso_origin_id.id])[0],
                'operating_unit_origin_id': history_data.get('operating_unit_origin_id', [contract.operating_unit_origin_id.id])[0],
                'inciso_dest_id': history_data.get('inciso_dest_id', [contract.inciso_dest_id.id])[0],
                'operating_unit_dest_id': history_data.get('operating_unit_dest_id', [contract.operating_unit_dest_id.id])[0],
                'date_start': history_data.get('date_start', contract.date_start),
                'date_end': history_data.get('date_end', contract.date_end),
                'date_end_commission': history_data.get('date_end_commission', contract.date_end_commission),
                'reason_description': history_data.get('reason_description', contract.reason_description),
                'reason_deregistration': history_data.get('reason_deregistration', contract.reason_deregistration),
                'income_mechanism_id': history_data.get('income_mechanism_id', [contract.income_mechanism_id.id])[0],
                'causes_discharge_id': history_data.get('causes_discharge_id', [contract.causes_discharge_id.id])[0],
                'extinction_commission_id': history_data.get('extinction_commission_id', [contract.extinction_commission_id.id])[0],
                'legajo_state_id': history_data.get('legajo_state_id', [contract.legajo_state_id.id])[0],
            }
        else:
            return {}
