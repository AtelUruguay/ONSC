# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _
from odoo.addons.ws_int_base.utils.service_registration import \
    register_service
from spyne import Boolean
from spyne import ComplexModel, ServiceBase
from spyne import rpc
from spyne.model.fault import Fault

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


class BaseComplexType(ComplexModel):
    __namespace__ = NAMESPACE_BASE_V1


class UsuarioNoAutorizado(Fault):
    __namespace__ = NAMESPACE_BASE_V1
    __type_name__ = 'UsuarioNoAutorizado'

    def __init__(self):
        super(UsuarioNoAutorizado, self). \
            __init__(faultcode='Server.005',
                     detail=_(
                         "Usuario no autorizado para la operacion."))


class PingResponse(BaseComplexType):
    _type_info = [
        ('PingResult', Boolean(min_occurs=1)),
    ]


class WsPrueba(ServiceBase):
    __wsse_conf__ = {
        'username': 'myusername',
        'password': 'mypassword'  # never store passwords directly in sources!
    }

    # Dependiendo de si se le pone la barra al final o no, el wsdl se debera
    # pedir con /?wsdl o no.
    __service_url_path__ = 'prueba_soap'
    __target_namespace__ = NAMESPACE_BASE_V1

    uid = 0

    @rpc(_body_style='bare', _returns=PingResponse)
    def ping(self):
        result = PingResponse()
        result.PingResult = True
        return result


register_service(WsPrueba, location_key='onsc_cv_digital.cv_digital_url')
