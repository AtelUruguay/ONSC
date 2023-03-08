# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital - Legajo',
    'version': '15.0.4.0.0',
    'summary': 'ONSC CV Digital - Legajo',
    'sequence': 11,
    'description': """
ONSC CV Digital - Legajo
====================
    """,
    'category': 'ONSC',
    'depends': ['onsc_cv_digital', 'hr', 'onsc_legajo'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/onsc_cv_digital_views.xml',
        'views/onsc_cv_hr_employee_views.xml',
        'views/onsc_cv_work_experience_views.xml',
        'views/onsc_legajo_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
