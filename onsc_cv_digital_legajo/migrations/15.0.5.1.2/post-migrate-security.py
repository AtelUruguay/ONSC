# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env['onsc.cv.digital'].search(
            [('type', '=', 'cv')]).with_context(is_legajo=True).button_legajo_update_documentary_validation_sections_tovalidate()
    except Exception:
        pass
