# -*- coding: utf-8 -*-
{
    'name': 'ONSC - HR Organizational Chart',
    'version': '15.0.3.2.1',
    'summary': 'ONSC - HR Organizational Chart',
    'description': 'ONSC - HR Organizational Chart',
    'category': 'ONSC',
    'depends': ['hr', 'onsc_catalog', 'model_history'],
    'data': [
        'security/onsc_catalog_organizational_chart_security.xml',
        'security/ir.model.access.csv',
        'wizard/views/onsc_organizational_wizard.xml',
        'views/org_chart_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'onsc_catalog_organizational_chart/static/src/js/primitives.js',
            'onsc_catalog_organizational_chart/static/src/js/pdfkitsamples.js',
            'onsc_catalog_organizational_chart/static/src/css/primitives.css',
            'onsc_catalog_organizational_chart/static/src/js/organizational_view.js',
            'onsc_catalog_organizational_chart/static/src/scss/chart_view.scss',
        ],
        'web.assets_qweb': [
            'onsc_catalog_organizational_chart/static/src/xml/chart_view.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
