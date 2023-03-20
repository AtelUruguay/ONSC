# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('onsc_cv_digital.group_user_cv').write({
        'implied_ids': [(3, env.ref('operating_unit.group_multi_operating_unit').id)]
    })
    env.ref('onsc_cv_digital.group_manager_cv').write({
        'implied_ids': [(3, env.ref('operating_unit.group_multi_operating_unit').id)]
    })
