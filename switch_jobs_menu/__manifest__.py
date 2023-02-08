# -*- coding: utf-8 -*-
{
    'name': 'Switch between jobs',
    'version': '15.0.1.0.0.',
    'summary': 'Allows you to switch between jobs available to the employee.',
    'sequence': 11,
    'description': """
Switch between jobs
====================
    """,
    'category': 'Tools',
    'depends': ['base', 'web', 'hr'],
    'data': [
    ],
    'assets': {
        'web.assets_qweb': [
            'switch_jobs_menu/static/src/js/*.xml',
        ],
        'web.assets_backend': [
            'switch_jobs_menu/static/src/js/*.js',
        ]
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
