# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Switch roles',
    'version': '15.0.1.0.0.',
    'summary': 'Assigns to the logged user the roles of the selected job position.',
    'sequence': 11,
    'description': """
Switch roles
====================
Assigns to the logged user the roles of the selected job position.
    """,
    'category': 'Tools',
    'depends': ['web', 'auth_oauth', 'website', 'switch_jobs_menu', 'base_user_role', 'hr_contract'],
    'data': [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
