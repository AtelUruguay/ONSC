# -*- coding: utf-8 -*-
import logging
from functools import wraps

from odoo import tools, _
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

try:
    from pyinstrument import Profiler
except Exception:
    Profiler = False
    _logger.warning("To use profile you need to install pyinstrument")


def profiler(func):
    """
    Decorator to print execution times in the log
    requirements:
        - pip install pyinstrument
        - add active_profiler=True in odoo.conf

    Example tu use:

    @profiler
    @api.model
    def create(self, vals):
        'your code here'




    :param func:
    :return:
    """
    _logger.warning("***********Profiling is active***********")
    active_profiler = tools.config.get('active_profiler', False)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if active_profiler:
            if not Profiler:
                raise MissingError("To use profile you need to install pyinstrument")
            new_profiler = Profiler()
            new_profiler.start()
        result = func(*args, **kwargs)
        if active_profiler:
            new_profiler.stop()
            with open('/tmp/profile_output.txt', 'w') as f:
                new_profiler.print(file=f)
        return result

    return wrapper


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
