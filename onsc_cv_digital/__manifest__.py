# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital',
    'version': '1.0',
    'summary': 'ONSC CV Digital',
    'sequence': 10,
    'description': """
ONSC CV Digital
====================
    """,
    'category': 'ONSC',
    'depends': ['base'],
    'data': [
        'security/onsc_cv_digital_security.xml',
        'security/ir.model.access.csv',
        'views/onsc_cv_document_type_views.xml',

        'views/onsc_cv_menuitems.xml',
    ],
    'demo': [
        'demo/onsc_cv_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
