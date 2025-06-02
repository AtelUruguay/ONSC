# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS11(models.AbstractModel):
    _name = 'onsc.legajo.abstract.baja.vl.ws11'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS11'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS11_bajaCS')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS11_9005")
        wsclient = self._get_client(parameter, '', integration_error)
        user_partner = self.env.user.partner_id
        cv_nro_doc_without_digit = user_partner.cv_nro_doc and user_partner.cv_nro_doc[:-1] or ''

        data = {
            'fechaVigencia': record.end_date.strftime('%d/%m/%Y'),
            'cedula': int(record.employee_id.cv_nro_doc[:-1]), 'descripcionMotivo': record.reason_description,
            'numeroNorma': record.norm_number, 'articuloNorma': record.norm_article,
            'tipoNormaSigla': record.norm_id.tipoNormaSigla, 'anioNorma': record.norm_year,
            'descripcionResolucion': record.resolution_description,
            'fechaResolucion': record.resolution_date.strftime('%d/%m/%Y'), 'tipoResolucion': record.resolution_type,
            'CodigoExtincionComision': int(record.extinction_commission_id.code),
            'usuarioCedulaOdoo': cv_nro_doc_without_digit
        }
        _logger.info('******************WS11')
        _logger.info(data)
        _logger.info('******************WS11')
        return self.with_context(baja_cs=record, log_info=log_info).suspend_security()._syncronize(wsclient, parameter,
                                                                                                   'WS11',
                                                                                                   integration_error,
                                                                                                   data)

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            baja_cs = self._context.get('baja_cs')
            onsc_legajo_integration_error_WS11_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS11_9004")
            try:
                baja_cs.action_actualizar_puesto()

            except Exception as e:
                long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='WS10', type='error',
                                    integration_log=onsc_legajo_integration_error_WS11_9004,
                                    long_description=long_description)
                baja_cs.write({
                    'is_error_synchronization': True, 'state': 'error_sgh',
                    'error_message_synchronization': long_description})

    def _process_servicecall_error(self, exception, origin_name, integration_error, long_description=''):
        baja_cs = self._context.get('baja_cs')
        baja_cs.write({
            'is_error_synchronization': True, 'state': 'communication_error',
            'error_message_synchronization': integration_error.description})
        super(ONSCLegajoAbstractSyncWS11, self)._process_servicecall_error(exception, origin_name, integration_error,
                                                                           long_description)

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        IntegrationError = self.env['onsc.legajo.integration.error']
        baja_cs = self._context.get('baja_cs')
        if hasattr(response, 'codigo'):
            result_error_code = response.codigo
            error = IntegrationError.search([('integration_code', '=', integration_error.integration_code),
                                             ('code_error', '=', str(result_error_code))], limit=1)
            self.create_new_log(origin=origin_name, type='error', integration_log=error or integration_error,
                                ws_tuple=False, long_description=response.mensaje)
            baja_cs.write({
                'is_error_synchronization': True, 'state': 'error_sgh',
                'error_message_synchronization': response.mensaje, })
        else:
            long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
            baja_cs.write({
                'is_error_synchronization': True, 'state': 'communication_error',
                'error_message_synchronization': long_description, })
            super(ONSCLegajoAbstractSyncWS11, self)._process_response_witherror(response,
                                                                                origin_name,
                                                                                integration_error,
                                                                                long_description)
