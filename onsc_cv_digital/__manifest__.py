# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital',
    'version': '1.1.2',
    'summary': 'ONSC CV Digital',
    'sequence': 10,
    'description': """
ONSC CV Digital
====================
    """,
    'category': 'ONSC',
    'depends': ['base', 'mail'],
    'data': [
        'security/onsc_cv_digital_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/onsc_cv_civil_status_data.xml',
        'data/onsc_cv_drivers_license_categories_data.xml',
        'data/onsc_cv_gender_data.xml',
        'data/onsc_cv_race_data.xml',
        'wizard/onsc_cv_reject_wizard_views.xml',
        'views/onsc_cv_document_type_views.xml',
        'views/onsc_cv_civil_status_views.xml',
        'views/onsc_cv_drivers_license_categories_views.xml',
        'views/onsc_cv_gender_views.xml',
        'views/onsc_cv_race_views.xml',
        'views/onsc_cv_location_views.xml',
        'views/res_country_views.xml',
        'views/onsc_cv_subinstitution_views.xml',
        'views/onsc_cv_institution_views.xml',
        'views/onsc_cv_menuitems.xml',
    ],
    'demo': [
        'demo/onsc_cv_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
