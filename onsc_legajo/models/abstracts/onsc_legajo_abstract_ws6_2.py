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
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS6_2_modificacionDatosFuncionario')
        WS6_2_9004 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS6_2_9004")
        WS6_2_9005 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS6_2_9005")
        wsclient = self._get_client(parameter, 'WS6.2', WS6_2_9005)

        Contract = self.env['hr.contract']
        with self._cr.savepoint():
            Contract.suspend_security().search([
                ('notify_sgh', '=', True),
                ('legajo_state', '=', 'baja')]).write({'notify_sgh': False})
            for record in Contract.suspend_security().search(
                    [('notify_sgh', '=', True), ('legajo_state', '!=', 'baja')]):
                try:
                    job = record.job_ids.filtered(lambda x: x.end_date is False)
                    if len(job) > 1:
                        job = job[0]
                    notify_partner = record.last_notify_user_id.partner_id
                    cv_nro_doc_without_digit = notify_partner.cv_nro_doc and notify_partner.cv_nro_doc[:-1] or ''
                    data = {
                        'cedula': int(record.employee_id.cv_nro_doc),
                        'secPlaza': int(record.sec_position),
                        'nroPlaza': record.workplace,
                        'idPuesto': record.position,
                        'usuarioCedulaOdoo': cv_nro_doc_without_digit
                    }
                    if job.department_id:
                        data.update({'uo': job.department_id.code})
                    if job.security_job_id:
                        data.update({'responsableUO': job.security_job_id.is_uo_manager and 'S' or 'N'})
                    if record.occupation_id:
                        data.update({'codigoOcupacion': record.occupation_id.code})

                    _logger.info('******************WS6.2')
                    _logger.info(data)
                    _logger.info('******************WS6.2')

                    self.with_context(contract=record, log_info=log_info).suspend_security()._syncronize(
                        wsclient,
                        parameter, 'WS6.2',
                        WS6_2_9004,
                        data)
                except Exception as e:
                    long_description = "Contrato: %s, Error al sincronizar WS6.2: %s" % (
                        record.display_name,
                        tools.ustr(e)
                    )
                    _logger.warning(long_description)
                    self.create_new_log(origin='WS6.2', type='error',
                                        integration_log=WS6_2_9004,
                                        long_description=long_description)

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
                self.create_new_log(origin='WS6.2', type='error',
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
            contract = self._context.get('contract')
            _long_description = 'Funcionario %s, %s' % (contract.display_name, response.mensaje)
            self.create_new_log(origin=origin_name, type='error', integration_log=error or integration_error,
                                ws_tuple=False, long_description=_long_description)

        else:
            long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."

            super(ONSCLegajoAbstractSyncWS6_2, self)._process_response_witherror(response,
                                                                                 origin_name,
                                                                                 integration_error,
                                                                                 long_description)
