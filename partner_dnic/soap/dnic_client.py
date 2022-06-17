# -*- coding: utf-8 -*-


import logging
import ssl

from suds import Client

from odoo import _
from odoo.exceptions import ValidationError

logging.getLogger('suds.client').setLevel(logging.DEBUG)


class DNICClient():

    def __init__(self, env):
        self.wsdl = env['ir.config_parameter'].sudo().get_param('partner_dnic.wsdl', False)
        self.timeout = 80

    def _create_unverified_https_context(self):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    def obtDocDigitalizadoService(self, NroIdentificacion,
                                  Nrodocumento=False,
                                  ClaveAcceso1=False,
                                  Organismo=False,
                                  IdSolicitud=False,
                                  TipoDocumento=False,
                                  NroSerie=False,
                                  ClaveAcceso2=False
                                  ):
        """
        Servicio de DNIC
        :param NroIdentificacion:
        :param Nrodocumento: Opcional
        :param ClaveAcceso1: Opcional
        :param Organismo:   Opcional
        :param IdSolicitud: Opcional
        :param TipoDocumento: Opcional
        :param NroSerie: Opcional
        :param ClaveAcceso2: Opcional
        :return:
        """
        if not self.wsdl:
            raise ValidationError(_("Debe configurar el parámetro del sistema con clave: partner_dnic.wsdl"
                                    " para la conexíon al servicio de DNIC"))

        self._create_unverified_https_context()
        client = Client(self.wsdl, timeout=self.timeout)
        if not client:
            raise ValidationError(_("No se pudo establecer la conexión con el servicio DNIC"))

        values = {'NroIdentificacion': NroIdentificacion}
        if Nrodocumento:
            values.update({'Nrodocumento': Nrodocumento})
        if ClaveAcceso1:
            values.update({'ClaveAcceso1': ClaveAcceso1})
        if Organismo:
            values.update({'Organismo': Organismo})
        if IdSolicitud:
            values.update({'IdSolicitud': IdSolicitud})
        if TipoDocumento:
            values.update({'TipoDocumento': TipoDocumento})
        if NroSerie:
            values.update({'NroSerie': NroSerie})
        if ClaveAcceso2:
            values.update({'ClaveAcceso2': ClaveAcceso2})
        request_param = {'paramObtDocDigitalizado': values}
        respuesta = client.service.obtDocDigitalizado(request_param)
        return self.procesarRespuesta(respuesta)

    def procesarRespuesta(self, respuesta):
        """return dict """
        result = {
            'cv_dnic_name_1': '',
            'cv_dnic_name_2': '',
            'cv_dnic_lastname_1': '',
            'cv_dnic_lastname_2': '',
            'cv_last_name_adoptive_1': '',
            'cv_last_name_adoptive_2': '',
            'cv_dnic_full_name': ''
        }
        return result
