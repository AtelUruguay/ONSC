# -*- coding: utf-8 -*-

# CONSULTA_DEUDA ERRORES
COMUNICACION_001 = {
    'type': 'COMUNICACION',
    'code': '001',
    'desc': u'Aplicativo caido o tiempo de espera agotado',
}

LOGIC_1011 = {
    'type': 'LOGIC',
    'code': '1011',
    'desc': u'El proceso de consulta de pagos ha tenido un comportamiento inesperado',
    'long_desc': u'Contacte con el administrador',
}

LOGIC_101 = {
    'type': 'LOGIC',
    'code': '101',
    'desc': u'No existe mapeo para el concepto',
}

LOGIC_102 = {
    'type': 'LOGIC',
    'code': '102',
    'desc': u'No existe mapeo para la UE',
}

LOGIC_103 = {
    'type': 'LOGIC',
    'code': '103',
    'desc': u'No existe mapeo para la Moneda',
}

LOGIC_104 = {
    'type': 'LOGIC',
    'code': '104',
    'desc': u'No existe cotización cargada para la moneda',
}

LOGIC_105 = {
    'type': 'LOGIC',
    'code': '105',
    'desc': u'No existe diario de tipo Pasarela',
}

LOGIC_106 = {
    'type': 'LOGIC',
    'code': '106',
    'desc': u'El monto del pago no coincide con el monto consultado',
}

LOGIC_107 = {
    'type': 'LOGIC',
    'code': '107',
    'desc': u'El identificador de la deuda no fué encontrado en el sistema',
}

LOGIC_108 = {
    'type': 'LOGIC',
    'code': '108',
    'desc': u'El mapeo del tipo de documento no es válido',
}

LOGIC_109 = {
    'type': 'LOGIC',
    'code': '109',
    'desc': u'No se ha podido generar la factura',
}

LOGIC_110 = {
    'type': 'LOGIC',
    'code': '110',
    'desc': u'No se ha podido generar el pago',
}

INTERNAL_XMLRPC_ERROR_CODE = "001"
INTERNAL_XMLRPC_DESC = "Internal XMLRPC error"
INTERNAL_XMLRPC_TYPE = "Server"
INTERNAL_XMLRPC_LONGDESC = "Please contact the administrator."

INVALID_USER_PASS_ERROR_CODE = "013"
INVALID_USER_PASS_DESC = "Invalid user/password"
INVALID_USER_PASS_TYPE = "Client"
INVALID_USER_PASS_LONGDESC = "Please specify a valid user/password."

DBNAME_HEADER_MISSING_ERROR_CODE = "018"
DBNAME_HEADER_MISSING_DESC = "dbname header is missing"
DBNAME_HEADER_MISSING_TYPE = "Client"
DBNAME_HEADER_MISSING_LONGDESC = "Please specify a valid dbname (header parameter: HTTP_DBNAME)."

DBNAME_HEADER_INVALID_ERROR_CODE = "023"
DBNAME_HEADER_INVALID_DESC = "dbname header is invalid"
DBNAME_HEADER_INVALID_TYPE = "Client"
DBNAME_HEADER_INVALID_LONGDESC = "Please specify a valid dbname. The value specified does not exist."

# INVOICE_NOT_FOUND_ERROR_CODE = "101"
# INVOICE_NOT_FOUND_DESC = "Invoice not found"
# INVOICE_NOT_FOUND_TYPE = "Client"
# INVOICE_NOT_FOUND_LONGDESC = "The fusion_id specified does not match with any invoice"

# MORE_THAN_ONE_INVOICE_FOUND_ERROR_CODE = "102"
# MORE_THAN_ONE_INVOICE_FOUND_DESC = "More than one invoice found"
# MORE_THAN_ONE_INVOICE_FOUND_TYPE = "Client"
# MORE_THAN_ONE_INVOICE_FOUND_LONGDESC = "The fusion_id specified matches with more than one invoice."

# OBTENER_ESTADO_3_EN_1_PARAMETERS_ERROR_CODE = "1001"
# OBTENER_ESTADO_3_EN_1_PARAMETERS_DESC = "Invalid parameters"
# OBTENER_ESTADO_3_EN_1_PARAMETERS_TYPE = "Client"
# OBTENER_ESTADO_3_EN_1_PARAMETERS_LONGDESC = "Please specify at least one parameter: invoice_id or fusion_id."
#
# ANULAR_ESTADO_3_EN_1_INVALID_STATE_ERROR_CODE = "1002"
# ANULAR_ESTADO_3_EN_1_INVALID_STATE_DESC = "Invalid state"
# ANULAR_ESTADO_3_EN_1_INVALID_STATE_TYPE = "Client"
# ANULAR_ESTADO_3_EN_1_INVALID_STATE_LONGDESC = "The invoice must be in state draft or cancel_siif in order to be available to be canceled."
#
#
# LINEAS_COSTO_DISTRIBUCION_INCONSISTENTES_ERROR_CODE = "2001"
# LINEAS_COSTO_DISTRIBUCION_INCONSISTENTES_DESC = "Sum of amount in distribution lines not equal to price_unit*quantity in product line"
# LINEAS_COSTO_DISTRIBUCION_INCONSISTENTES_TYPE = "Client"
# LINEAS_COSTO_DISTRIBUCION_INCONSISTENTES_LONGDESC = "Sum of amount in distribution lines not equal to price_unit*quantity in product line. Please correct and send again."


