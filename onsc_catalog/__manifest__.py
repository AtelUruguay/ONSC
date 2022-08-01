# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Catálogos',
    'version': '15.0.1.0.0.',
    'summary': 'ONSC - Catálogos',
    'sequence': 11,
    'description': """
ONSC - Catálogos
====================
    """,
    'category': 'ONSC',
    'depends': ['hr', 'mail', 'operating_unit','model_history'],
    'data': [
        'security/onsc_catalog_security.xml',
        'security/ir.model.access.csv',
        'views/onsc_catalog_inciso_views.xml',
        'views/operating_unit_views.xml',
        'views/onsc_catalog_menuitems.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
