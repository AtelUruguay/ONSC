# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital - Legajo Auth',
    'version': '15.0.1.0.0',
    'summary': 'ONSC CV Digital - Legajo Auth',
    'sequence': 11,
    'description': """
ONSC CV Digital - Legajo Auth
====================
    """,
    'category': 'ONSC',
    'depends': ['onsc_cv_digital_legajo', 'onsc_cv_digital_auth'],
    'data': [
        'security/onsc_cv_digital_legajo_security.xml',
        'views/onsc_legajo_views.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
