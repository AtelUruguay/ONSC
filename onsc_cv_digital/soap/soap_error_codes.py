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

# LOGICA
LOGIC_150 = {
    'type': 'LOGICA',
    'code': '150',
    'desc': u'Error',
    'long_desc': u'Contacte con el administrador',
}

LOGIC_151 = {
    'type': 'LOGICA',
    'code': '151',
    'desc': u'Código del País no identificado',
    'long_desc': u'',
}

LOGIC_151_1 = {
    'type': 'LOGICA',
    'code': '151',
    'desc': u'Código del País no identificado',
    'long_desc': u'Fórmato inválido, la longitud adecuada es 2',
}

LOGIC_152 = {
    'type': 'LOGICA',
    'code': '152',
    'desc': u'Tipo de documento no identificado',
    'long_desc': u'',
}

LOGIC_153 = {
    'type': 'LOGICA',
    'code': '153',
    'desc': u'No se ha identificado un CV activo en el sistema',
    'long_desc': u'',
}

LOGIC_154 = {
    'type': 'LOGICA',
    'code': '154',
    'desc': u'Parámetro acción no es válido. Los valores permitidos son: P,R,C',
    'long_desc': u'',
}

LOGIC_155 = {
    'type': 'LOGICA',
    'code': '155',
    'desc': u'No se ha identificado un CV activo para este llamado',
    'long_desc': u'',
}

LOGIC_156 = {
    'type': 'LOGICA',
    'code': '156',
    'desc': u'No se ha podido identificar el llamado o la postulación',
    'long_desc': u'',
}

LOGIC_157 = {
    'type': 'LOGICA',
    'code': '157',
    'desc': u'El llamado ya se encuentra cerrado',
    'long_desc': u'',
}

LOGIC_158 = {
    'type': 'LOGICA',
    'code': '158',
    'desc': u'Las copias del llamado ya han sido enviadas',
    'long_desc': u'',
}
