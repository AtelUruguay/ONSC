# -*- coding: utf-8 -*-
{
    'name': 'Partner DNIC Integration',
    'version': '1.0',
    'license': '',
    'author': "Quanam",
    'website': "https://www.quanam.com",
    'description': """
Partner DNIC Integration
=====================================================

""",
    'depends': ['base', 'base_setup'],
    'data': [
        'views/res_config_settings_view.xml',
    ],
    'external_dependencies': {
        'python': ['unidecode', 'suds-py3'],
    }
}
