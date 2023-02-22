# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Base',
    'version': '15.0.5.0.0',
    'summary': 'ONSC - Base',
    'sequence': 11,
    'description': """
ONSC - Base
====================
    """,
    'category': 'ONSC',
    'depends': ['base', 'web_responsive', 'website', 'auth_iduy_primary_login'],
    'data': [
        'security/onsc_base_security.xml',
        'security/ir.model.access.csv',
        'views/onsc_log_views.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
