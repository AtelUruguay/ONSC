# -*- coding: utf-8 -*-
from odoo import _


def get_onchange_warning_response(message, notif_type='notification'):
    return {
        'warning': {
            'title': _("Atención"),
            'type': notif_type,
            'message': message
        },
    }


def filter_str2float(str, float_separator=','):
    result = ''
    for letter in str:
        if letter.isdigit() or letter in (float_separator, '.'):
            result += letter
    return result
