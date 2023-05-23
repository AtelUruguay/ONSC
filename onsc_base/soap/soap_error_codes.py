# -*- coding: utf-8 -*-
# pylint: skip-file
from spyne.model.fault import Fault


def _raise_fault(error):
    raise Fault(
        error.get('code'),
        error.get('desc', ''),
        error.get('type', ''),
        error.get('long_desc', ''),
    )


# CREDENCIALES
AUTH_50 = {
    'type': 'AUTH',
    'code': '50',
    'desc': u'Error desconocido al autenticarse en Odoo',
    'long_desc': u'Contacte con el administrador',
}
AUTH_51 = {
    'type': 'AUTH',
    'code': '51',
    'desc': u'Credenciales inválidas',
    'long_desc': u'Contacte con el administrador',
}
AUTH_52 = {
    'type': 'AUTH',
    'code': '52',
    'desc': u'Formato del AUTHORIZATION inválido o inexistente',
    'long_desc': u'Contacte con el administrador',
}
AUTH_53 = {
    'type': 'AUTH',
    'code': '53',
    'desc': u'DBNAME inexistente',
    'long_desc': u'Contacte con el administrador',
}

LOGIC_150 = {
    'type': 'LOGICA',
    'code': '150',
    'desc': u'Error',
    'long_desc': u'Contacte con el administrador',
}