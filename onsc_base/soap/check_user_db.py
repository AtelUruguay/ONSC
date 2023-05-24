# -*- coding: utf-8 -*-
# pylint: disable=incoherent-interpreter-exec-perm

import logging

import odoo
from basicauth import decode

from . import soap_error_codes

_logger = logging.getLogger(__name__)


class CheckUserDBName():
    def check_user_dbname(self, transport):
        wsgi_env = transport.req_env

        authorization = wsgi_env.get('HTTP_AUTHORIZATION', None)
        dbname = wsgi_env.get('HTTP_DBNAME', None)
        _logger.debug("Authorization: ", authorization)
        _logger.debug("dbname: ", dbname)

        try:
            if authorization is None:
                return soap_error_codes._raise_fault(soap_error_codes.AUTH_50)
            username, pwd = decode(authorization)
        except Exception:
            return soap_error_codes._raise_fault(soap_error_codes.AUTH_52)
        if dbname is None:
            return soap_error_codes._raise_fault(soap_error_codes.AUTH_53)
        try:
            res_users = odoo.registry(dbname)['res.users']
            uid = res_users.authenticate(dbname, username, pwd, {})
        except Exception:
            return soap_error_codes._raise_fault(soap_error_codes.AUTH_51)
        return (uid, pwd, dbname)
