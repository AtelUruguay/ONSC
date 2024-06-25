# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        # OCULTANDO INFORME ESTANDAR EN FUNCIONARIO: IMPRIMIR INSIGNIA
        hr_employee_print_badge_report = env.ref('hr.hr_employee_print_badge')
        hr_employee_print_badge_report.unlink_action()
    except Exception:
        pass
