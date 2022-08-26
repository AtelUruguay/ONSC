# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital - Catálogo',
    'version': '15.0.1.0.0.',
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
        'views/onsc_cv_digital_views.xml',
        'views/onsc_catalog_validators_inciso_ue.xml'

    ],
    'external_dependencies': {}
}
