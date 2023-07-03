# -*- coding: utf-8 -*-

import logging

from odoo import models, api, tools

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS6_2(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws6.2'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS6.2'

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('parameter_onsc_legajo_WS6_2')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_errorWS6_2_9005")

        wsclient = self._get_client(parameter, 'WS6.2', integration_error)

        Contract = self.env['hr.contract']
        for record in Contract.suspend_security().search([('notify_sgh', '=', True)]):
            Job = record.job_ids.filtered(lambda x: x.end_date is False)
            data = {
                'cedula': int(record.employee_id.cv_nro_doc[:-1], 16),
                'secPlaza': int(record.sec_position),
                'nroPlaza': record.workplace,
                'uo': Job.department_id and Job.department_id.code or None,
                'responsableUO': Job.security_job_id and 'S' if Job.security_job_id.is_uo_manager else 'N' or None,
                'codigoOcupacion': record.occupation_id and record.occupation_id.code or None,
            }
            return self.with_context(contract=record, log_info=log_info).suspend_security()._syncronize(
                wsclient,
                parameter, 'WS6.2',
                integration_error,
                data)

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            contract = self._context.get('contract')
            onsc_legajo_integration_error_WS6_2_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS6_2_9004")
            try:
                contract.write({'notify_sgh': False})

            except Exception as e:
                long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='WS6.1', type='error',
                                    integration_log=onsc_legajo_integration_error_WS6_2_9004,
                                    long_description=long_description)

    def _process_servicecall_error(self, exception, origin_name, integration_error, long_description=''):

        super(ONSCLegajoAbstractSyncWS6_2, self)._process_servicecall_error(exception, origin_name, integration_error,
                                                                            long_description)

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        IntegrationError = self.env['onsc.legajo.integration.error']
        if hasattr(response, 'codigo'):
            result_error_code = response.codigo
            error = IntegrationError.search([('integration_code', '=', integration_error.integration_code),
                                             ('code_error', '=', str(result_error_code))], limit=1)
            self.create_new_log(origin=origin_name, type='error', integration_log=error or integration_error,
                                ws_tuple=False, long_description=response.mensaje)

        else:
            long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."

            super(ONSCLegajoAbstractSyncWS6_2, self)._process_response_witherror(response,
                                                                                 origin_name,
                                                                                 integration_error,
                                                                                 long_description)
