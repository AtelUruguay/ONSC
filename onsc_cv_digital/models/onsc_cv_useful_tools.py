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
    reject_reason_header_message = """<ul style="margin:0px 0 12px 0;box-sizing:border-box;">%s</ul>"""
    reject_reason_body_message = ""
    for catalog in conditional_catalog_list:
        recordset_field = eval('record.%s' % catalog)
        catalog_state = recordset_field and recordset_field.state or False
        if catalog_state == 'rejected':
            _state['state'] = 'rejected'
            reject_reason_body_message += "<li><b>%s</b>: %s</li>" % (recordset_field._description,
                                                                      recordset_field.reject_reason)
        elif catalog_state == 'to_validate' and _state.get('state') == 'validated':
            _state['state'] = 'to_validate'
    if _state.get('state') == 'rejected':
        _state['reject_reason'] = reject_reason_header_message % reject_reason_body_message
    return _state
