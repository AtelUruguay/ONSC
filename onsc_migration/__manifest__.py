# -*- coding: utf-8 -*-
{
    'name': 'ONSC Migracion',
    'version': '15.0.10.0.0',
    'summary': 'ONSC Migracion',
    'sequence': 11,
    'description': """
ONSC Migracion
====================
    """,
    'category': 'ONSC',
    'depends': ['onsc_cv_digital_legajo'],
    'data': [
        'security/onsc_migration_security.xml',
        'security/ir.model.access.csv',
        'views/onsc_migration_views.xml',
        'views/onsc_migration_menuitems.xml',

    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
