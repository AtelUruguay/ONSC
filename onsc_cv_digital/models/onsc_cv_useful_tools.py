# -*- coding: utf-8 -*-

def _get_validation_status(record, conditional_catalog_list):
    """
    :param str record: Odoo recodset sobre el que se desea conocer el Estado de Catálogos condicionales
    :param list conditional_catalog_list: Cada elemento constituye un Catalogo condicional (i.e. ['institution_id', 'subinstitution_id'])

    :rtype: dict: Estado de Catálogos condicionales final para el recordset y Motivo de rechazo en caso de existir
                (i.e. {'state': 'rejected', 'reject_reason': 'Aqui va el motivo del rechazo'})
    """
    if len(record) > 1:
        return False
    _state = {'state': 'validated', 'reject_reason': ''}
    for catalog in conditional_catalog_list:
        catalog_state = eval('record.%s.state' % catalog)
        if catalog_state == 'rejected':
            return {'state': 'rejected', 'reject_reason': eval('record.%s.reject_reason' % catalog)}
        if catalog_state == 'to_validate' and _state.get('state') == 'validated':
            _state['state'] = 'to_validate'
    return _state
