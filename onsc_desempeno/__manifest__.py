# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Gestión de Desempeño',
    'version': '15.0.4.6.0',
    'summary': 'ONSC - Gestión de Desempeño',
    'sequence': 1,
    'description': """
ONSC - Gestión de Desempeño
====================
    """,
    'category': 'ONSC',
    'depends': ['mail',  'model_history', 'base_suspend_security', 'onsc_base', 'onsc_catalog'],
    'data': [
        'security/onsc_desempeno_security.xml',
        'security/ir.model.access.csv',
        'views/catalogs/onsc_desempeno_dimension_views.xml',
        'views/catalogs/onsc_desempeno_skill_views.xml',
        'views/catalogs/onsc_desempeno_level_views.xml',
        'views/catalogs/onsc_desempeno_degree_views.xml',
        'views/catalogs/onsc_desempeno_degree_progress_views.xml',
        'views/catalogs/onsc_desempeno_development_means_views.xml',
        'views/catalogs/onsc_desempeno_reason_change_evaluator_views.xml',
        'views/onsc_desempeno_menuitems.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
