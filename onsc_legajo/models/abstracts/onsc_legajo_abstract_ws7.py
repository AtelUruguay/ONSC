# -*- coding: utf-8 -*-

import logging

from odoo import models, api, tools

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS7(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws7'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS7'

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS7_F_PU_RVE_MOVIMIENTOS')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS7_9005")
        wsclient = self._get_client(parameter, 'WS7', integration_error)
        data = {
            'paFechaDesde': '03/05/2022 00:00:00',
            'paFechaHasta': '05/05/2022 00:00:00'
        }
        return self.with_context(log_info=log_info, simpleWsdl=True).suspend_security()._syncronize(
            wsclient,
            parameter,
            'WS7',
            integration_error,
            data)

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            onsc_legajo_integration_error_WS7_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS7_9004")
            Contract = self.env['hr.contract'].sudo()
            try:
                for operation in response[:2]:
                    if operation.tipo_mov == 'ALTA':
                        self._check_alta(Contract, operation, onsc_legajo_integration_error_WS7_9004)
            except Exception as e:
                long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='WS7', type='error',
                                    integration_log=onsc_legajo_integration_error_WS7_9004,
                                    long_description=long_description)

    def _check_alta(self, Contract, operation, error):
        if Contract.search_count([
            ('inciso_id.budget_code', '=', str(operation.inciso)),
            ('operating_unit_id.budget_code', '=', str(operation.ue)),
            ('position', '=', str(operation.idPuesto)),
            ('workplace', '=', operation.nroPlaza),
            ('sec_position', '=', operation.secPlaza),
            # ('emissor_country_id.code_rve', '=', str(operation.ue)),
            # ('document_type_id.code', '=', str(tipo_doc)),
            ('nro_doc', '=', str(operation.doc)),
        ]) == 0:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Alta no encontrada')

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

            super(ONSCLegajoAbstractSyncWS7, self)._process_response_witherror(response,
                                                                               origin_name,
                                                                               integration_error,
                                                                               long_description)
