# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('onsc_catalog.group_catalog_aprobador_cgn').write({
        'implied_ids': [(3, env.ref('operating_unit.group_multi_operating_unit').id)]
    })
    env.ref('onsc_catalog.group_catalog_configurador_servicio_civil').write({
        'implied_ids': [(3, env.ref('operating_unit.group_manager_operating_unit').id)]
    })

    cr.execute("DELETE FROM operating_unit_users_rel WHERE user_id NOT IN (1,2,4,5,6,7)")
    cr.execute("DELETE FROM res_company_users_rel WHERE cid <> 1 AND user_id > 7")
