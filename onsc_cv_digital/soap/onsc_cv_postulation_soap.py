# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import odoo
from odoo import api, SUPERUSER_ID
from odoo.addons.ws_int_base.utils.service_registration import register_service
from odoo.modules.registry import Registry
from spyne import ServiceBase, ComplexModelBase, ComplexModel
from spyne import Unicode, DateTime
from spyne import rpc
from spyne.model.complex import Array
from spyne.model.fault import Fault

from . import soap_error_codes
from .validar_usuario_y_db import validar_usuario_y_db

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


class BaseComplexType(ComplexModelBase):
    __namespace__ = NAMESPACE_BASE_V1


class ErrorHandler(ComplexModel):
    __type_name__ = 'error_handler'
    _type_info = [
        ('type', Unicode(min_occurs=1)),
        ('code', Unicode(min_occurs=1)),
        ('error', Unicode(min_occurs=1)),
        ('description', Unicode(min_occurs=1)),
    ]
    _type_info_alt = []


class WsCVPostulacionResponse(BaseComplexType):
    __type_name__ = 'service_response'
    _type_info = {
        'result': Unicode(min_occurs=1),
        'errors': Array(ErrorHandler, min_occurs=0, type_name='ArrayOfErrorHandler')
    }
    _type_info_alt = []


class WsCVPostulacionRequest(ComplexModel):
    __type_name__ = 'service_request'
    __namespace__ = NAMESPACE_BASE_V1

    _type_info = [
        ('codPais', Unicode(min_occurs=1)),
        ('tipoDoc', Unicode(min_occurs=1)),
        ('nroDoc', Unicode(min_occurs=1)),
        ('fechaPostulacion', DateTime(min_occurs=1)),
        ('nroPostulacion', Unicode(min_occurs=1)),
        ('nroLlamado', Unicode(min_occurs=1)),
        ('accion', Unicode(min_occurs=1)),
    ]


class WsCVPostulacion(ServiceBase):
    __service_url_path__ = 'postulacion'
    __target_namespace__ = NAMESPACE_BASE_V1

    @rpc(WsCVPostulacionRequest.customize(nullable=False, min_occurs=1),
         _body_style='bare',
         _returns=WsCVPostulacionResponse)
    def postulacion(self, request):
        try:
            (integration_uid, pwd, dbname) = validar_usuario_y_db().val_usuario_y_db(self.transport)
            dbname = list(Registry.registries.d)[0]
            uid = SUPERUSER_ID
            registry = odoo.registry(dbname)
            cr = registry.cursor()
            env = api.Environment(cr, uid, {})
            parameter = env['ir.config_parameter'].sudo().get_param('parameter_ws_postulation_user')
            if env['res.users'].sudo().browse(integration_uid).login != parameter:
                soap_error_codes._raise_fault(soap_error_codes.AUTH_51)

        except Fault as e:
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVPostulacionResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        except Exception as e:
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVPostulacionResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        try:
            env['onsc.cv.digital.call']._create_postulation(
                request.codPais,
                request.tipoDoc,
                request.nroDoc,
                request.fechaPostulacion,
                request.nroPostulacion,
                request.nroLlamado,
                request.accion)
            return WsCVPostulacionResponse(result='ok', errors=[])
        except Fault as e:
            cr.rollback()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVPostulacionResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        except Exception as e:
            cr.rollback()
            logic_150_extended = soap_error_codes.LOGIC_150
            if hasattr(e, 'name') and isinstance(e.name, str):
                logic_150_extended['long_desc'] = e.name
            e = soap_error_codes._raise_fault(logic_150_extended)
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVPostulacionResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        finally:
            cr.commit()
            cr.close()


register_service(WsCVPostulacion)
