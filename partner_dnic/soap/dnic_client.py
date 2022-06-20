# -*- coding: utf-8 -*-


import logging
import re
import ssl

from suds import Client

from odoo import _
from odoo.exceptions import ValidationError

logging.getLogger('suds.client').setLevel(logging.DEBUG)


def normalize_str(s):
    """Elimina espacios adicionales en el string"""
    if s and isinstance(s, str):
        return re.sub(' +', ' ', s)
    return s


class DNICClient():

    def __init__(self, company):
        self.wsdl = company.dnic_wsdl
        self.dnic_organization = company.dnic_organization
        self.dnic_password = company.dnic_password
        self.dnic_doc_type = company.dnic_doc_type
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

    def ObtPersonaPorDoc(self, Nrodocumento):
        """
        Servicio de DNIC
        :param Nrodocumento: Requerido
        :return:
        """
        if not self.wsdl:
            raise ValidationError(_("Debe configurar el parámetro del sistema con clave: partner_dnic.wsdl"
                                    " para la conexíon al servicio de DNIC"))

        self._create_unverified_https_context()
        client = Client(self.wsdl, timeout=self.timeout)
        if not client:
            raise ValidationError(_("No se pudo establecer la conexión con el servicio DNIC"))

        values = {
            'Organizacion': self.dnic_organization,
            'PasswordEntidad': self.dnic_password,
            'Nrodocumento': Nrodocumento,
            'TipoDocumento': self.dnic_doc_type,
        }

        respuesta = client.service.ObtPersonaPorDoc(values)
        return self.procesarRespuesta(respuesta)

    def procesarRespuesta(self, respuesta):
        """return dict """
        result = {}
        if hasattr(respuesta, 'Errores'):
            errors = [x[1][0] for x in respuesta.Errores]
            raise ValidationError(
                '/n'.join([str(x.CodMensaje) + '-' + x.DatoExtra + '-' + x.Descripcion for x in errors]))
        elif hasattr(respuesta, 'ObjPersona'):

            result_aux = {
                'cv_dnic_name_1': respuesta.ObjPersona.Nombre1,
                'cv_dnic_name_2': respuesta.ObjPersona.Nombre2,
                'cv_dnic_lastname_1': respuesta.ObjPersona.Apellido1,
                'cv_dnic_lastname_2': respuesta.ObjPersona.Apellido2,
                'cv_last_name_adoptive_1': respuesta.ObjPersona.ApellidoAdoptivo1,
                'cv_last_name_adoptive_2': respuesta.ObjPersona.ApellidoAdoptivo2,
                'cv_dnic_full_name': respuesta.ObjPersona.NombreEnCedula,
                'cv_birthdate': respuesta.ObjPersona.FechaNacimiento,
                'cv_sex': respuesta.ObjPersona.Sexo

            }
            result = {k: normalize_str(v) for k, v in result_aux.items()}
        return result
