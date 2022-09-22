# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital - Catálogo',
    'version': '15.0.2.0.0.',
    'license': '',
    'author': "Quanam",
    'website': "https://www.quanam.com",
    'description': """
ONSC CV Digital - Catálogo
=====================================================

""",
    'depends': ['onsc_cv_digital', 'onsc_catalog'],
    'data': [
        'security/onsc_cv_digital_catalog_security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameters_data.xml',
        'views/onsc_cv_digital_views.xml',
        'views/onsc_catalog_validators_inciso_ue.xml',
        'views/onsc_cv_digital_call_views.xml',
        'views/onsc_catalog_menuitems.xml',
    ],
    'external_dependencies': {}
}
