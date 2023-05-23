# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.onsc_base.soap import soap_error_codes as onsc_error_codes
from odoo.addons.onsc_base.soap.check_user_db import CheckUserDBName
from odoo.addons.onsc_base.soap.onsc_base_soap import ErrorHandler, WsResponse
from odoo.addons.ws_int_base.utils.service_registration import register_service
from spyne import ServiceBase, ComplexModel
from spyne import Unicode
from spyne import rpc
from spyne.model.fault import Fault

import odoo
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
from . import soap_error_codes as legajo_error_codes

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


class WsLegajoWS5Request(ComplexModel):
    __type_name__ = 'service_request'
    __namespace__ = NAMESPACE_BASE_V1

    _type_info = [
        ('pdaId', Unicode(min_occurs=1)),
        ('codResult', Unicode(min_occurs=1)),
    ]


class WsCVPostulacion(ServiceBase):
    __service_url_path__ = 'legajo_ws5'
    __target_namespace__ = NAMESPACE_BASE_V1

    @rpc(WsLegajoWS5Request.customize(nullable=False, min_occurs=1),
         _body_style='bare',
         _returns=WsResponse)
    def legajo_ws5(self, request):
        # pylint: disable=invalid-commit
        try:
            cr = False
            (integration_uid, pwd, dbname) = CheckUserDBName().check_user_dbname(self.transport)
            dbname = list(Registry.registries.d)[0]
            uid = SUPERUSER_ID
            registry = odoo.registry(dbname)
            cr = registry.cursor()
            env = api.Environment(cr, uid, {})
            parameter = env['ir.config_parameter'].sudo().get_param('parameter_ws5_user')
            if env['res.users'].sudo().browse(integration_uid).login != parameter:
                onsc_error_codes._raise_fault(onsc_error_codes.AUTH_51)
        except Fault as e:
            if cr:
                cr.rollback()
                cr.close()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        except Exception as e:
            if cr:
                cr.rollback()
                cr.close()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response

        try:
            alta_vl = env['onsc.legajo.alta.vl'].search([
                ('id_alta', '=', request.pdaId),
                ('state', '=', 'pendiente_auditoria_cgn')], limit=1)
            # alta_vl = env['onsc.legajo.alta.vl'].search([
            #     ('id', '=', 60)], limit=1)
            if not alta_vl:
                onsc_error_codes._raise_fault(legajo_error_codes.LOGIC_151)
            if request.codResult == 'aprobada':
                alta_vl._aprobado_cgn()
            elif request.codResult == 'rechazada':
                alta_vl._rechazado_cgn()
            else:
                onsc_error_codes._raise_fault(legajo_error_codes.LOGIC_152)
            cr.commit()
            return WsResponse(result='ok', errors=[])
        except Fault as e:
            cr.rollback()
            error_item = ErrorHandler(code=e.faultcode, type=e.faultactor, error=e.faultstring, description=e.detail)
            response = WsResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        except Exception as e:
            cr.rollback()
            logic_150_extended = onsc_error_codes.LOGIC_150
            if hasattr(e, 'name') and isinstance(e.name, str):
                logic_150_extended['long_desc'] = e.name
            error_item = ErrorHandler(code=logic_150_extended.get('code'),
                                      type=logic_150_extended.get('type'),
                                      error=logic_150_extended.get('desc'),
                                      description=logic_150_extended.get('long_desc'))
            response = WsResponse(result='error', errors=[])
            response.errors.append(error_item)
            return response
        finally:
            cr.close()


register_service(WsCVPostulacion)
