# -*- coding: utf-8 -*-
{
    'name' : 'ONSC CV Digital',
    'version' : '1.0',
    'summary': 'ONSC CV Digital',
    'sequence': 10,
    'description': """
ONSC CV Digital
====================
    """,
    'category': 'ONSC',
    'depends' : ['base'],
    'data': [
        'security/onsc_cv_digital_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
