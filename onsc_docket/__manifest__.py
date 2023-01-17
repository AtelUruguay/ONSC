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
        'data/onsc_docket_state_square_data.xml',
        'data/onsc_docket_reason_extinction_commission_data.xml',
        'data/onsc_docket_commission_regime_data.xml',
        'views/catalogs/onsc_catalog_base_views.xml',
        'views/catalogs/onsc_docket_health_provider_views.xml',
        'views/catalogs/onsc_docket_document_type_views.xml',
        'views/catalogs/onsc_docket_income_mechanism_views.xml',
        'views/catalogs/onsc_docket_causes_discharge_views.xml',
        'views/catalogs/onsc_docket_integration_error_views.xml',
        'views/catalogs/onsc_docket_reason_extinction_commission_views.xml',
        'views/catalogs/onsc_docket_commission_regime_views.xml',
        'views/catalogs/onsc_docket_state_square_views.xml',
        'views/catalogs/onsc_docket_commission_regime_views.xml',
        'views/catalogs/onsc_docket_job_type_views.xml',
        'views/onsc_docket_menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
