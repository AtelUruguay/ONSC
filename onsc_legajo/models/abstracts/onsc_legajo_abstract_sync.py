# -*- coding: utf-8 -*-

from odoo import models, tools, _

from ...soap import soap_client


class ONSCLegajoAbstractSync(models.AbstractModel):
    _name = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS externos'

    def _get_client(self, parameter, origin_name, integration_error):
        ONSCLegajoClient = soap_client.ONSCLegajoClient()
        try:
            return ONSCLegajoClient.get_client(origin_name, parameter)
        except Exception as e:
            self.create_new_log(
                origin=origin_name,
                type='error',
                integration_log=integration_error,
                ws_tuple=False,
                long_description=tools.ustr(e))
            return

    def _syncronize(self, client, parameter, origin_name, integration_error, values=False):
        IntegrationError = self.env['onsc.legajo.integration.error']
        ONSCLegajoClient = soap_client.ONSCLegajoClient()
        try:
            response = ONSCLegajoClient.get_response(client, parameter, values, self._context.get('simpleWsdl', False))
        except Exception as e:
            self._process_servicecall_error(e, origin_name, integration_error)
            altas_vl = self._context.get('altas_vl', self.env['onsc.legajo.alta.vl'])
            altas_vl.write({
                'is_error_synchronization': True,
                'state': 'error_sgh',
                'error_message_synchronization': "Error devuelto por SGH: " + tools.ustr(e)
            })
            return "Error devuelto por SGH: " + tools.ustr(e)
        if hasattr(response, 'servicioResultado'):
            if response.servicioResultado.codigo == 0:
                return self._populate_from_syncronization(response)
            else:
                error = IntegrationError.search([
                    ('integration_code', '=', integration_error.integration_code),
                    ('code_error', '=', str(response.servicioResultado.codigo))
                ], limit=1)
                long_description = '%s - Código: %s' % (
                    tools.ustr(response.servicioResultado.mensaje), str(response.servicioResultado.codigo))
                self._process_response_witherror(
                    response,
                    origin_name,
                    error or integration_error,
                    long_description
                )
                return long_description
        elif hasattr(response, 'codigoResultado'):
            if response.codigoResultado == 0:
                return self._populate_from_syncronization(response)
            else:
                error = IntegrationError.search([
                    ('integration_code', '=', integration_error.integration_code),
                    ('code_error', '=', str(response.codigoResultado))
                ], limit=1)
                long_description = '%s - Código: %s' % (
                    tools.ustr(response.mensajeResultado), str(response.codigoResultado))
                self._process_response_witherror(
                    response,
                    origin_name,
                    error or integration_error,
                    long_description
                )
                return long_description
        elif hasattr(response, 'codigo'):
            if response.codigo == 0:
                return self._populate_from_syncronization(response)
            else:
                error = IntegrationError.search([
                    ('integration_code', '=', integration_error.integration_code),
                    ('code_error', '=', str(response.codigo))
                ], limit=1)
                long_description = '%s - Código: %s' % (
                    tools.ustr(response.mensaje), str(response.codigo))
                self._process_response_witherror(
                    response,
                    origin_name,
                    error or integration_error,
                    long_description
                )
                return long_description
        elif len(response) > 0 and isinstance(response, list):
            return self._populate_from_syncronization(response)
        return "No se obtuvo respuesta del WS"

    def _populate_from_syncronization(self, response):
        return True

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        return self.create_new_log(
            origin=origin_name,
            type='error',
            integration_log=integration_error,
            ws_tuple=False,
            long_description=long_description
        )

    def _process_servicecall_error(self, exception, origin_name, integration_error, long_description=''):
        self.create_new_log(
            origin=origin_name,
            type='error',
            integration_log=integration_error,
            ws_tuple=False,
            long_description=tools.ustr(exception))

    # pylint: disable=redefined-builtin
    def create_new_log(self, origin, type, integration_log, ws_tuple=False, long_description=False):
        if long_description and ws_tuple:
            _long_description = _('%s Tupla: %s') % (long_description, str(ws_tuple))
        elif not ws_tuple:
            _long_description = long_description
        else:
            _long_description = _('Tupla: %s') % (str(ws_tuple))
        log = self.env['onsc.log'].create({
            'process': 'legajo',
            'origin': origin,
            'type': type,
            'ref': integration_log.integration_code,
            'code': integration_log.code_error,
            'description': integration_log.description,
            'long_description': _long_description
        })
        return log
