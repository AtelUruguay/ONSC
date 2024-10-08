# -*- coding: utf-8 -*-
{
    'name': 'ONSC CV Digital - Desempeno',
    'version': '15.0.27.0.0',
    'summary': 'ONSC CV Digital - Desempeno',
    'sequence': 11,
    'description': """
ONSC CV Digital - Desempeno
====================
    """,
    'category': 'ONSC',
    'depends': ['onsc_cv_digital_legajo','onsc_desempeno'],
    'data': [
        'data/onsc_legajo_report_config_data.xml',
        'report/legajo_report_sections/onsc_legajo_report_section_funct_info.xml',
        'report/onsc_legajo_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
