import logging

import openerp.tools
from basicauth import decode

from . import soap_error_codes


class validar_usuario_y_db():
    def val_usuario_y_db(self, transport):
        wsgi_env = transport.req_env

        authorization = wsgi_env.get('HTTP_AUTHORIZATION', None)
        dbname = wsgi_env.get('HTTP_DBNAME', None)
        print("Authorization: ", authorization)
        print("dbname: ", dbname)

        try:
            if authorization is None:
                return soap_error_codes._raise_fault(soap_error_codes.AUTH_50)
            username, pwd = decode(authorization)
        except Exception as e:
            return soap_error_codes._raise_fault(soap_error_codes.AUTH_52)
        if dbname is None:
            return soap_error_codes._raise_fault(soap_error_codes.AUTH_53)
        try:
            res_users = openerp.registry(dbname)['res.users']
            uid = res_users.authenticate(dbname, username, pwd, {})
        except Exception as e:
            logging.exception('')
            return soap_error_codes._raise_fault(soap_error_codes.AUTH_51)
        return (uid, pwd, dbname)
