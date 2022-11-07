# -*- coding: utf-8 -*-
{
    'name': 'ONSC - HR Organizational Chart',
    'version': '15.0.2.0.0',
    'summary': 'ONSC - HR Organizational Chart',
    'description': 'ONSC - HR Organizational Chart',
    'category': 'ONSC',
    'depends': ['hr', 'onsc_catalog'],
    'data': [
        'security/onsc_catalog_organizational_chart_security.xml',
        'security/ir.model.access.csv',
        'data/onsc_catalog_organizational_chart_data.xml',
        'wizard/views/onsc_organizational_wizard.xml',
        'views/org_chart_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'onsc_catalog_organizational_chart/static/src/js/jquery.orgchart.js',
            'onsc_catalog_organizational_chart/static/src/css/jquery.orgchart.css',
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
