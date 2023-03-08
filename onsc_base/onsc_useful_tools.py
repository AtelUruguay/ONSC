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


def filter_str2float(original_str, float_separator=','):
    result = ''
    for letter in original_str:
        if letter.isdigit() or letter in (float_separator, '.'):
            result += letter
    return result

def calc_full_name(first_name, second_name, last_name_1, last_name_2):
    name_values = [first_name,
                   second_name,
                   last_name_1,
                   last_name_2]
    return ' '.join([x for x in name_values if x])
