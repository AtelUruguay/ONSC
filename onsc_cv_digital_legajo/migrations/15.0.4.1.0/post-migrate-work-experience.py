# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        for record in env['onsc.cv.work.experience'].search([('causes_discharge_id', '!=', False)]):
            record.causes_discharge = record.causes_discharge_id.name
    except Exception:
        pass
