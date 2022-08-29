# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import odoo
from odoo import _
from odoo import api, SUPERUSER_ID
from odoo.addons.ws_int_base.utils.service_registration \
    import register_service
from odoo.exceptions import UserError as InternalError
from odoo.modules.registry import Registry
from spyne import ServiceBase, ComplexModelBase
from spyne import Unicode, Array, DateTime
from spyne import rpc
from spyne.model.fault import Fault

from .validar_usuario_y_db import validar_usuario_y_db

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


class BaseComplexType(ComplexModelBase):
    __namespace__ = NAMESPACE_BASE_V1


class UsuarioNoAutorizado(Fault):
    __namespace__ = NAMESPACE_BASE_V1
    __type_name__ = 'UsuarioNoAutorizado'

    def __init__(self):
        super(UsuarioNoAutorizado, self). \
            __init__(faultcode='Server.005',
                     detail=_(
                         "Usuario no autorizado para la operacion."))


class ErrorHandler(BaseComplexType):
    _type_info = {
        'codigo': Unicode(min_occurs=1),
        'descripcion': Unicode(min_occurs=1),
    }
    _type_info_alt = []


class WsCVPostulacionResponse(BaseComplexType):
    _type_info = {
        'result': Unicode(min_occurs=1),
        'menssages': Array(ErrorHandler, min_occurs=0, type_name='ArrayOfErrorHandler')
    }
    _type_info_alt = []


class WsCVPostulacion(ServiceBase):
    __service_url_path__ = 'postulacion'
    __target_namespace__ = NAMESPACE_BASE_V1
    # __wsse_conf__ = {
    #     'username': 'myusername',
    #     'password': 'mypassword'  # never store passwords directly in sources!
    # }

    uid = 0

    @rpc(Unicode, Unicode, Unicode, DateTime, Unicode, Unicode, Unicode, _returns=WsCVPostulacionResponse)
    def postulacion(
            self, codPais, tipoDoc, nroDoc, fechaPostulacion, nroPostulacion, nroLlamado, accion
    ):
        (uid, pwd, dbname) = validar_usuario_y_db().val_usuario_y_db(self.transport)
        dbname = list(Registry.registries.d)[0]
        uid = SUPERUSER_ID
        try:
            registry = odoo.registry(dbname)
            cr = registry.cursor()
            env = api.Environment(cr, uid, {})
            return WsCVPostulacionResponse(
                result='ok',
            )
        except Fault as e:
            cr.rollback()
            raise InternalError(e)
        except Exception as e:
            cr.rollback()
            raise InternalError(e)
        finally:
            cr.commit()
            cr.close()


register_service(WsCVPostulacion)
