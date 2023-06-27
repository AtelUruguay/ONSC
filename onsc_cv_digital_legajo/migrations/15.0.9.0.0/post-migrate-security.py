# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env['onsc.cv.digital'].search([('type', '=', 'cv')]).validate_header_documentary_validation()
    except Exception as e:
        pass
