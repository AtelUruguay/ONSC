# -*- coding: utf-8 -*-
{
    'name': 'ONSC - HR Organizational Chart',
    'version': '15.0.1.0.0',
    'summary': 'UO organizational chart',
    'description': 'UO organizational chart',
    'category': 'ONSC',
    'depends': ['hr', 'onsc_catalog'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/views/onsc_organizational_wizard.xml',
        'views/org_chart_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'onsc_catalog_organizational_chart/static/src/js/tree_maker.js',
            # 'onsc_catalog_organizational_chart/static/src/js/html2canvas.js',
            'onsc_catalog_organizational_chart/static/src/js/jquery.orgchart.js',
            # 'onsc_catalog_organizational_chart/static/src/js/jquery.connectingLine.js',
            # 'onsc_catalog_organizational_chart/static/src/js/jquery.svg.min.js',
            # 'onsc_catalog_organizational_chart/static/src/js/jquery.html-svg-connect.js',
            'onsc_catalog_organizational_chart/static/src/css/jquery.orgchart.css',
            # 'onsc_catalog_organizational_chart/static/src/css/tree_maker.css',
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
