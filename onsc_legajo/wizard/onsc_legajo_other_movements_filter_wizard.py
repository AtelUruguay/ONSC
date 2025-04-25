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

    @api.onchange('inciso_id', 'operating_unit_id')
    def _onchange_inciso_operating_unit(self):
        self.date_from = False
        self.date_to = False


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
        return self.user_has_groups('onsc_legajo.group_legajo_report_other_movements_consult')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_other_movements_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_other_movements_ue')

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
            'token': _token,
        }
        self._set_info(
            _token,
            self.date_from,
            self.date_to)
        action['domain'] = [('token', '=', _token)]
        action['context'] = new_context
        return action

    def _get_base_sql(self, date_from, date_to):
        _sql1 = """
            SELECT doc as nro_doc,
            regexp_replace(
                trim(
                  COALESCE(primer_nombre, '') || ' ' ||
                  COALESCE(segundo_nombre, '') || ' ' ||
                  COALESCE(primer_ap, '') || ' ' ||
                  COALESCE(segundo_ap, '')
                ),
                '\s+', ' ', 'g'
              ) AS employee,
          mov as move_type,
          fecha_aud as audit_date,
          CASE 
                WHEN tipo_mov ='ALTA' THEN inciso_id
          END AS inciso_id,
          CASE 
                WHEN tipo_mov ='ALTA' THEN operating_unit_id
          END AS operating_unit_id,
          CASE 
                WHEN tipo_mov ='ALTA' THEN 
                  regexp_replace(
                        trim(
                          COALESCE("idPuesto", '') || ' _ ' ||
                          COALESCE("nroPlaza", '') || ' _ ' ||
                          COALESCE("secPlaza", '') 
                        ),
                        '\s+', ' ', 'g'
                      )  
            END AS puesto_plaza,
            CASE 
                WHEN tipo_mov ='ALTA' THEN regime_id
            END AS regime_id,
            CASE 
                WHEN tipo_mov ='ALTA' THEN descriptor1_id
            END AS descriptor1_id,
            CASE 
                WHEN tipo_mov ='ALTA' THEN descriptor2_id
            END AS descriptor2_id,
            CASE 
                WHEN tipo_mov ='ALTA' THEN descriptor3_id
            END AS descriptor3_id,
            CASE 
                WHEN tipo_mov ='ALTA' THEN descriptor4_id
            END AS descriptor4_id,
            CASE 
                WHEN tipo_mov ='ALTA' THEN retributive_day_id
            END AS retributive_day_id,
            CASE 
                WHEN tipo_mov ='ALTA' THEN fecha_ing_adm
            END AS public_admin_entry_date,
            CASE 
                WHEN tipo_mov ='ALTA' THEN "fechaGraduacion"
            END AS graduation_date,
            CASE 
                WHEN tipo_mov ='ALTA' THEN marital_status_id
            END AS marital_status_id,
            CASE 
                WHEN tipo_mov ='BAJA' THEN operating_unit_id
            END AS operating_unit_origin_id,
            CASE 
                WHEN tipo_mov ='BAJA' THEN operating_unit_id
            END AS operating_unit_origin_id,
             CASE 
                WHEN tipo_mov ='ALTA' THEN 
                  regexp_replace(
                        trim(
                          COALESCE("idPuesto", '') || ' _ ' ||
                          COALESCE("nroPlaza", '') || ' _ ' ||
                          COALESCE("secPlaza", '') 
                        ),
                        '\s+', ' ', 'g'
                      )  
            END AS puesto_plaza_origin,
            CASE 
                WHEN tipo_mov ='BAJA' THEN regime_id
            END AS regime_origin_id,
            CASE 
                WHEN tipo_mov ='BAJA' THEN descriptor1_id
            END AS descriptor1_origin_id,
            CASE 
                WHEN tipo_mov ='BAJA' THEN descriptor2_id
            END AS descriptor2_origin_id,
            CASE 
                WHEN tipo_mov ='BAJA' THEN descriptor3_id
            END AS descriptor3_origin_id,
            CASE 
                WHEN tipo_mov ='BAJA' THEN descriptor4_id
            END AS descriptor4_origin_id
            
         
        
        FROM onsc_legajo_staging_ws7 
        WHERE state='processed'
        AND mov in ('ASCENSO', 'TRANSFORMA', 'REESTRUCTURA','DESRESERVA','RESERVA')
        AND fecha_vig ::DATE BETWEEN '%s' AND '%s'
    """ % (date_from, date_to)

        return _sql1
    def _get_record_job_vals(self, record, job_dict):
        return {
            'department_id': job_dict.get('department_id', False),
        }

    def _set_info(self, token, date_from, date_to, contract_id):
        LegajoUtils = self.env['onsc.legajo.utils']

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
            transaction_date = result.get('transaction_date') and result.get('transaction_date') or fields.Date.today()
            contract_data = LegajoUtils._get_historical_contract_data(result, transaction_date)
            for key, value in contract_data.items():
                new_record[key] = value
            new_record['report_user_id'] = user_id
            new_record['token'] = token
            new_record.pop('id')
            new_record.pop('eff_date')

            bulked_vals.append(new_record)
        result = self.env['onsc.legajo.other.movements'].sudo().create(bulked_vals)
        return result
