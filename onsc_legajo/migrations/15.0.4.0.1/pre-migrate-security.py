# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        role_base = env.ref('__import__.ONSC_Rol_Base')
        role_user_cv = env.ref('__import__.ONSC_Usuario_CV')
        list_users = env.ref('base.user_admin')
        list_users |= env.ref('base.public_user')
        list_users |= env.ref('base.user_root')
        for user in env['res.users'].with_context(active_test=False).search([('id', 'not in', list_users.ids)]):
            user.write({
                'role_line_ids': [
                    (5,),
                    (0, 0, {'role_id': role_base.id}),
                    (0, 0, {'role_id': role_user_cv.id})
                ]})

    except Exception as e:
        pass
