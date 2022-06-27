# -*- coding: utf-8 -*-
from odoo import _


def get_help_online_action(help_url):
    if help_url:
        return {
            'name': _("Ayuda en línea"),
            'type': 'ir.actions.act_url',
            'url': help_url,
            'target': 'new',
        }
    else:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("No se ha encontrado la ayuda en línea"),
                'type': 'info',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
