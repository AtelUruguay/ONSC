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
        ONSCLegajoClient = soap_client.ONSCLegajoClient()
        try:
            response = ONSCLegajoClient.get_response(client, parameter, values)
        except Exception as e:
            self.create_new_log(
                origin=origin_name,
                type='error',
                integration_log=integration_error,
                ws_tuple=False,
                long_description=tools.ustr(e))
            return
        if hasattr(response, 'servicioResultado'):
            if response.servicioResultado.codigo == 0:
                return self._populate_from_syncronization(response)
            else:
                self.create_new_log(
                    origin=origin_name,
                    type='error',
                    integration_log=integration_error,
                    ws_tuple=False,
                    long_description='%s - Código: %s' % (
                        tools.ustr(response.servicioResultado.mensaje), str(response.servicioResultado.codigo)))
        elif hasattr(response, 'codigoResultado'):
            if response.codigoResultado == 0:
                return self._populate_from_syncronization(response, values)
            else:
                self.create_new_log(
                    origin=origin_name,
                    type='error',
                    integration_log=integration_error,
                    ws_tuple=False,
                    long_description='%s - Código: %s' % (
                        tools.ustr(response.mensajeResultado), str(response.codigoResultado)))
        return True

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
