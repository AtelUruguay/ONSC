# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Catálogos',
    'version': '15.0.4.4.1',
    'summary': 'ONSC - Catálogos',
    'sequence': 11,
    'description': """
ONSC - Catálogos
====================
    """,
    'category': 'ONSC',
    'depends': ['hr', 'mail', 'operating_unit', 'model_history', 'base_suspend_security', 'onsc_base'],
    'data': [
        'security/onsc_catalog_security.xml',
        'security/ir.model.access.csv',

        'data/onsc_catalog_data.xml',

        'views/catalogs/onsc_catalog_base_views.xml',
        'views/onsc_catalog_inciso_views.xml',
        'views/operating_unit_views.xml',
        'views/hr_department_views.xml',
        'views/onsc_catalog_occupation_views.xml',

        'views/catalogs/onsc_catalog_occupational_family_views.xml',
        'views/catalogs/onsc_catalog_management_process_views.xml',
        'views/catalogs/onsc_catalog_descriptors.xml',
        'views/onsc_catalog_menuitems.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
