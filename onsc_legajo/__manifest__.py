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
    'depends': ['onsc_base', 'onsc_catalog','base_user_role'],
    'data': [
        'security/onsc_legajo_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/onsc_legajo_state_square_data.xml',
        'data/onsc_legajo_reason_extinction_commission_data.xml',
        'data/onsc_legajo_commission_regime_data.xml',
        'views/catalogs/onsc_legajo_emergency_views.xml',
        'views/catalogs/onsc_legajo_health_provider_views.xml',
        'views/catalogs/onsc_legajo_document_type_views.xml',
        'views/catalogs/onsc_legajo_income_mechanism_views.xml',
        'views/catalogs/onsc_legajo_causes_discharge_views.xml',
        'views/catalogs/onsc_legajo_integration_error_views.xml',
        'views/catalogs/onsc_legajo_reason_extinction_commission_views.xml',
        'views/catalogs/onsc_legajo_commission_regime_views.xml',
        'views/catalogs/onsc_legajo_state_square_views.xml',
        'views/catalogs/onsc_legajo_commission_regime_views.xml',
        'views/catalogs/onsc_legajo_job_type_views.xml',
        'views/catalogs/onsc_legajo_base_views.xml',
        'views/onsc_legajo_menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
