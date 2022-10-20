# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'HR Organizational Chart',
    'version': '15.0.1.0.0',
    'summary': 'HR Employees organizational chart',
    'description': 'HR Employees organizational chart',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'live_test_url': 'https://youtu.be/dyCzplsAysQ',
    'category': 'Generic Modules/Human Resources',
    'website': "https://www.openhrms.com",
    'depends': ['hr', 'onsc_catalog'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/views/onsc_organizational_wizard.xml',
        'views/org_chart_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_organizational_chart/static/src/js/tree_maker.js',
            'hr_organizational_chart/static/src/js/html2canvas.js',
            'hr_organizational_chart/static/src/js/jquery.orgchart.js',
            'hr_organizational_chart/static/src/css/jquery.orgchart.css',
            'hr_organizational_chart/static/src/css/tree_maker.css',
            'hr_organizational_chart/static/src/js/organizational_view.js',
            'hr_organizational_chart/static/src/scss/chart_view.scss',
        ],
        'web.assets_qweb': [
            'hr_organizational_chart/static/src/xml/chart_view.xml',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
