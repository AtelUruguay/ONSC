# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS9(models.AbstractModel):
    _name = 'onsc.legajo.abstract.baja.vl.ws9'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS9'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS9_bajaSGH')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS9_9005")
        wsclient = self._get_client(parameter, '', integration_error)

        for vl in record.employment_relationship_ids.filtered(lambda x: x.selected):
            data = {
                'fechaDeBaja': record.end_date.strftime('%d/%m/%Y'),
                'descripcionMotivo': record.reason_description,
                'numeroNorma': record.norm_number,
                'articuloNorma': record.norm_article,
                'tipoNormaSigla': record.norm_id.tipoNormaSigla,
                'anioNorma': record.norm_year,
                'descripcionResolucion': record.resolution_description,
                'fechaResolucion': record.resolution_date.strftime('%d/%m/%Y'),
                'tipoResolucion': record.resolution_type,
                'cedula': int(record.partner_id.cv_nro_doc[:-1], 16),
                'secPlaza': int(vl.secPosition),
                'estadoLaboralBaja': int(record.causes_discharge_id.code_cgn)
            }
            _logger.info('******************WS9')
            _logger.info(data)
            _logger.info('******************WS9')
            return self.with_context(baja_vl=record, log_info=log_info).suspend_security()._syncronize(
                wsclient,
                parameter, 'WS9',
                integration_error,
                data)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            baja_vl = self._context.get('baja_vl')
            onsc_legajo_integration_error_WS9_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS9_9004")
            if not hasattr(response, 'servicioResultado'):
                self.create_new_log(
                    origin='WS9',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS9_9004,
                    long_description="No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
                )
                return "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
            if response.pdaId:
                try:
                    baja_vl.write({
                        'id_baja': response.pdaId,
                        'is_error_synchronization': False,
                        'state': 'pendiente_auditoria_cgn',
                        'error_message_synchronization': False,
                    })
                    return response.pdaId
                except Exception as e:
                    long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                    _logger.warning(long_description)
                    self.create_new_log(
                        origin='WS9',
                        type='error',
                        integration_log=long_description
                    )
                    baja_vl.write({
                        'id_baja': False,
                        'is_error_synchronization': True,
                        'state': 'error_sgh',
                        'error_message_synchronization': long_description,
                    })
            else:
                long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
                self.create_new_log(
                    origin='WS9',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS9_9004,
                    long_description=long_description
                )
                baja_vl.write({
                    'id_baja': False,
                    'is_error_synchronization': True,
                    'state': 'error_sgh',
                    'error_message_synchronization': long_description,
                })
                
    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        IntegrationError = self.env['onsc.legajo.integration.error']
        baja_vl = self._context.get('baja_vl')
        if hasattr(response, 'servicioResultado'):
            result_error_code = response.servicioResultado.codigo
            error = IntegrationError.search([
                ('integration_code', '=', integration_error.integration_code),
                ('code_error', '=', str(result_error_code))
            ], limit=1)
            self.create_new_log(
                origin=origin_name,
                type='error',
                integration_log=error or integration_error,
                ws_tuple=False,
                long_description=response.servicioResultado.mensaje)
            baja_vl.write({
                'id_baja': False,
                'is_error_synchronization': True,
                'state': 'error_sgh',
                'error_message_synchronization': response.servicioResultado.mensaje,
            })
        else:
            long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
            baja_vl.write({
                'id_baja': False,
                'is_error_synchronization': True,
                'state': 'error_sgh',
                'error_message_synchronization': long_description,
            })
            super(ONSCLegajoAbstractSyncWS9, self)._process_response_witherror(
                response,
                origin_name,
                integration_error,
                long_description
            )
