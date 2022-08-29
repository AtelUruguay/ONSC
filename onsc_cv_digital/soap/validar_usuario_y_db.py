import logging
import sys

import openerp.tools
from basicauth import decode
from spyne.model.fault import Fault

from . import soap_error_codes


class validar_usuario_y_db():
    def val_usuario_y_db(self, transport):
        wsgi_env = transport.req_env

        authorization = wsgi_env.get('HTTP_AUTHORIZATION', None)
        dbname = wsgi_env.get('HTTP_DBNAME', None)
        print("Authorization: ", authorization)
        print("dbname: ", dbname)

        if authorization is not None:
            username, pwd = decode(authorization)
        else:
            raise Fault(soap_error_codes.INVALID_USER_PASS_ERROR_CODE, soap_error_codes.INVALID_USER_PASS_DESC,
                        soap_error_codes.INVALID_USER_PASS_TYPE, soap_error_codes.INVALID_USER_PASS_LONGDESC)

        if dbname is None:
            raise Fault(soap_error_codes.DBNAME_HEADER_MISSING_ERROR_CODE, soap_error_codes.DBNAME_HEADER_MISSING_DESC,
                        soap_error_codes.DBNAME_HEADER_MISSING_TYPE,
                        soap_error_codes.DBNAME_HEADER_MISSING_LONGDESC)

        # Get the uid
        try:

            res_users = openerp.registry(dbname)['res.users']
            uid = res_users.authenticate(dbname, username, pwd, {})

            # sock_common = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/common')
            # uid = sock_common.login(dbname, username, pwd)
            print
            "UID obtenido: ", uid
        except:
            logging.exception('')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_value.faultCode.find("does not exist") != -1:
                raise Fault(soap_error_codes.DBNAME_HEADER_INVALID_ERROR_CODE,
                            soap_error_codes.DBNAME_HEADER_INVALID_DESC,
                            soap_error_codes.DBNAME_HEADER_INVALID_TYPE,
                            soap_error_codes.DBNAME_HEADER_INVALID_LONGDESC)
            else:
                raise Fault(soap_error_codes.INTERNAL_XMLRPC_ERROR_CODE, soap_error_codes.INTERNAL_XMLRPC_DESC,
                            soap_error_codes.INTERNAL_XMLRPC_TYPE,
                            soap_error_codes.INTERNAL_XMLRPC_LONGDESC)

        return (uid, pwd, dbname)
