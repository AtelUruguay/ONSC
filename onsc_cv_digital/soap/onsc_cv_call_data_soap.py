# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

import odoo
from odoo import api, SUPERUSER_ID
from odoo.addons.ws_int_base.utils.service_registration import register_service
from odoo.modules.registry import Registry
from spyne import ServiceBase, ComplexModel
from spyne import Unicode
from spyne import rpc
from spyne.model.complex import Array
from spyne.model.fault import Fault

from . import soap_error_codes
from .check_user_db import CheckUserDBName
from .onsc_cv_base_soap import ErrorHandler, WsCVResponse

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


class WsCVDatosLlamadoPostulacionRequest(ComplexModel):
    __type_name__ = 'datos_llamado_postulacion'
    __namespace__ = NAMESPACE_BASE_V1
    _type_info = [
        ('nroPostulacion', Unicode(min_occurs=1)),
    ]
    _type_info_alt = []


class WsCVDatosLlamadoRequest(ComplexModel):
    __type_name__ = 'service_request'
    __namespace__ = NAMESPACE_BASE_V1

    _type_info = {
        'nroLlamado': Unicode(min_occurs=1),
        'postulaciones': Array(WsCVDatosLlamadoPostulacionRequest,
                               min_occurs=1,
                               type_name='ArrayOfWsCVDatosLlamadoPostulacionRequest')
    }


class WsCVDatosLlamado(ServiceBase):
    __service_url_path__ = 'datosLlamado'
    __target_namespace__ = NAMESPACE_BASE_V1

    @rpc(WsCVDatosLlamadoRequest.customize(nullable=False, min_occurs=1),
         _body_style='bare',
         _returns=WsCVResponse)
    def datosLlamado(self, request):
        # pylint: disable=invalid-commit
        try:
            cr = False
            (integration_uid, pwd, dbname) = CheckUserDBName().check_user_dbname(self.transport)
            dbname = list(Registry.registries.d)[0]
            uid = SUPERUSER_ID
            registry = odoo.registry(dbname)
            cr = registry.cursor()
            env = api.Environment(cr, uid, {})
            parameter = env['ir.config_parameter'].sudo().get_param('parameter_ws_postulation_user')
            if env['res.users'].sudo().browse(integration_uid).login != parameter:
                soap_error_codes._raise_fault(soap_error_codes.AUTH_51)

        except Fault as e:
            if cr:
                cr.rollback()
                cr.close()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        except Exception as e:
            if cr:
                cr.rollback()
                cr.close()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response

        try:
            postulations = []
            for element in request.postulaciones:
                postulations.append(element.nroPostulacion)
            env['onsc.cv.digital.call'].call_preselection(request.nroLlamado, postulations)
            cr.commit()
            return WsCVResponse(result='ok', errors=[])
        except Fault as e:
            cr.rollback()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsCVResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        except Exception as e:
            cr.rollback()
            logic_150_extended = soap_error_codes.LOGIC_150
            if hasattr(e, 'name') and isinstance(e.name, str):
                logic_150_extended['long_desc'] = e.name
            error_item = ErrorHandler(code=logic_150_extended.get('code'),
                                      type=logic_150_extended.get('type'),
                                      error=logic_150_extended.get('desc'),
                                      description=logic_150_extended.get('long_desc'))
            response = WsCVResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        finally:
            cr.close()


register_service(WsCVDatosLlamado)
