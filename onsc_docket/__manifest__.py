# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Legajo',
    'version': '15.0.0.0.0',
    'summary': 'ONSC - Legajo',
    'sequence': 11,
    'description': """
ONSC - Legajo
====================
    """,
    'category': 'ONSC',
    'depends': ['onsc_base', 'onsc_catalog'],
    'data': [
        'security/ir.model.access.csv',
        'views/catalogs/onsc_docket_emergency_views.xml',
        'views/catalogs/onsc_docket_health_provider_views.xml',
        'views/catalogs/onsc_docket_document_type_views.xml',
        'views/catalogs/onsc_docket_income_mechanism_views.xml',
        'views/catalogs/onsc_docket_causes_discharge_views.xml',
        'views/catalogs/onsc_docket_base_views.xml',
        'views/onsc_docket_menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
