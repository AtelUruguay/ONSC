# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital - Legajo',
    'version': '15.0.12.3.0',
    'summary': 'ONSC CV Digital - Legajo',
    'sequence': 11,
    'description': """
ONSC CV Digital - Legajo
====================
    """,
    'category': 'ONSC',
    'depends': ['onsc_cv_digital', 'hr', 'onsc_legajo', 'onsc_cv_digital_catalog'],
    'data': [
        'security/onsc_cv_digital_legajo_security.xml',
        'security/onsc_cv_digital_legajo_rules.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/res_partner_views.xml',
        'views/onsc_cv_documentary_validation_config_views.xml',
        'views/onsc_cv_digital_views.xml',
        'views/onsc_cv_hr_employee_views.xml',
        'views/onsc_cv_work_experience_views.xml',
        'views/onsc_cv_digital_validation_views.xml',
        'views/onsc_legajo_views.xml',
        'views/onsc_legajo_alta_vl_views.xml',
        'views/onsc_legajo_mass_upload_alta_vl.xml',
        'views/onsc_legajo_alta_cs_view.xml',
        'views/onsc_cv_digital_legajo_menuitems.xml',
        'report/onsc_cv_digital_report.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
