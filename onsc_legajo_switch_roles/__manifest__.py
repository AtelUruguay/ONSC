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
    'depends': ['web', 'auth_oauth', 'website', 'switch_jobs_menu', 'base_user_role', 'onsc_legajo'],
    'data': [
        'views/res_user_role_views.xml',
        'views/res_user_role_views.xml',
        'views/onsc_legajo_security_job_views.xml',
        'views/hr_job_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
