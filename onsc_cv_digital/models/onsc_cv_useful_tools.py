# -*- coding: utf-8 -*-
import re
from odoo import _
import requests
from odoo.addons.phone_validation.tools import phone_validation


def get_validation_status(record, conditional_catalog_list):
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
        catalog_state_list = list(map(lambda x: x.state, recordset_field))
        if list(filter(lambda x: x == 'rejected', catalog_state_list)):
            _state['state'] = 'rejected'
            reject_reason_body_message += "<li><b>%s</b>: %s</li>" % (recordset_field._description,
                                                                      recordset_field.reject_reason)
        elif list(filter(lambda x: x == 'to_validate', catalog_state_list)) and _state.get('state') == 'validated':
            _state['state'] = 'to_validate'
    if _state.get('state') == 'rejected':
        _state['reject_reason'] = reject_reason_header_message % reject_reason_body_message
    return _state


def is_valid_url(url):
    if 'http://' not in url and 'https://' not in url:
        url = '%s%s' % ('http://', url)
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    result = url is not None and regex.search(url)
    if not result:
        regex = re.compile(
            r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)',
            re.IGNORECASE)
        return regex.search(url)
    return result


def is_exist_url(url):
    try:
        if 'http://' not in url and 'https://' not in url:
            url = '%s%s' % ('http://', url)
        return requests.get(url).status_code == 200
    except requests.exceptions.SSLError:
        return True
    except Exception:
        return False


def get_onchange_warning_response(message, notif_type='notification'):
    return {
        'warning': {
            'title': _("Atención"),
            'type': notif_type,
            'message': message
        },

    }


def is_valid_email(email):
    expression = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    return re.match(expression, email) is not None


def get_phone_format(self, number, country=None, force_format='INTERNATIONAL'):
    country = country or self.country_id
    if not country:
        return number
    return phone_validation.phone_format(
        number,
        country.code if country else None,
        country.phone_code if country else None,
        force_format,
        raise_exception=False
    )
