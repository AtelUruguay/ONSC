# -*- coding: utf-8 -*-


import logging
import ssl

from suds.client import Client as SUDSClient
from zeep import Client as ZeepClient

from odoo import _
from odoo.exceptions import ValidationError

logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

_logger = logging.getLogger(__name__)


class ONSCLegajoClient():

    def __init__(self):
        self.timeout = 60

    def _create_unverified_https_context(self):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    def get_client(self, name, ws_url, pass_location=False, use_zeep=False):
        """
        """
        self._create_unverified_https_context()

        if not ws_url:
            raise ValidationError(
                _("Parámetro del sistema para la integración %s no está establecido. "
                  "El formato esperado es: wsdl;método") % (
                    name))
        ws_url_splitted = ws_url.split(';')
        if len(ws_url_splitted) != 2:
            raise ValidationError(
                _("Parámetro del sistema %s para la integración %s no está bien configurado. "
                  "El formato esperado es: wsdl;método") % (
                    ws_url, name))
        wsdl = ws_url_splitted[0]
        if use_zeep:
            client = ZeepClient(wsdl)
        elif pass_location:
            client = SUDSClient(wsdl, location=wsdl, timeout=self.timeout)
        else:
            client = SUDSClient(wsdl, timeout=self.timeout)
        if not client:
            raise ValidationError(_("No se pudo establecer la conexión con el servicio"))
        return client

    def get_response(self, client, ws_url, values, simpleWsdl=False, use_execute_with_args=False):
        """
        """
        ws_url_splitted = ws_url.split(';')
        method = ws_url_splitted[1]
        if len(values) and not simpleWsdl:
            url = 'client.service.%s(values)' % method
        elif use_execute_with_args:
            return self.execute_service_with_args(client, values)
        elif len(values):
            simple_params = []
            for key, value in values.items():
                if isinstance(value, str):
                    simple_params.append("%s = '%s'" % (key, value))
                elif isinstance(value, int):
                    simple_params.append("%s = %s" % (key, value))
            simple_param_str = ', '.join(simple_params)
            url = "client.service.%s(%s)" % (method, simple_param_str)
        else:
            url = 'client.service.%s()' % method
        _logger.warning('*********WS Request**********')
        _logger.warning(url)
        result = eval(url)
        return result

    def execute_service_with_args(self, client, args_dict):
        _logger.warning('*********WS Request**********')
        _logger.warning("client.service.Execute(**args_dict) - args_dict: %s" % args_dict)
        return client.service.Execute(**args_dict)
