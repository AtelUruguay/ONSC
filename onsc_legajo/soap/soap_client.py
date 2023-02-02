# -*- coding: utf-8 -*-


import logging
import ssl

from odoo import _
from odoo.exceptions import ValidationError
from suds.client import Client

logging.getLogger('suds.client').setLevel(logging.DEBUG)


class ONSCLegajoClient():

    def __init__(self):
        self.timeout = 20

    def _create_unverified_https_context(self):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    def get_response(self, ws_url, values):
        """
        """
        self._create_unverified_https_context()

        ws_url_splitted = ws_url.split(';')
        if len(ws_url_splitted) != 2:
            raise ValidationError(
                _("Parámetro del sistema %s no está bien configurado. El formato esperado es: wsdl;método") % ws_url)
        wsdl = ws_url_splitted[0]
        method = ws_url_splitted[1]
        client = Client(wsdl, timeout=self.timeout)
        if not client:
            raise ValidationError(_("No se pudo establecer la conexión con el servicio"))

        respuesta = eval('client.service.%s(values)' % method)
        return respuesta
