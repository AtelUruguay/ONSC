# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital Auth',
    'version': '15.0.4.0.0',
    'license': '',
    'author': "Quanam",
    'website': "https://www.quanam.com",
    'description': """
ONSC CV Digital Auth
=====================================================

""",
    'depends': ['auth_iduy_primary_login', 'partner_dnic', 'onsc_cv_digital'],
    'data': [
        'views/res_partner_view.xml',
        'views/onsc_cv_digital_views.xml',

    ],
    'external_dependencies': {
        'python': ['unidecode'],
    }
}
