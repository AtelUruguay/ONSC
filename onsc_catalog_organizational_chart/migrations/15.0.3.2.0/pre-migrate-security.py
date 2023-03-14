# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('onsc_catalog_organizational_chart.group_catalog_consulta_organigrama').write({
        'implied_ids': [(3, env.ref('operating_unit.group_multi_operating_unit').id)]
    })
