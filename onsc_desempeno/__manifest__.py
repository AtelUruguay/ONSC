# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Gestión de Desempeño',
    'version': '15.0.5.0.0',
    'summary': 'ONSC - Gestión de Desempeño',
    'sequence': 1,
    'description': """
ONSC - Gestión de Desempeño
====================
    """,
    'category': 'ONSC',
    'depends': ['mail', 'model_history', 'base_suspend_security' , 'onsc_base',
                'onsc_catalog', 'onsc_legajo'],
    'data': [
        'security/onsc_desempeno_security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/catalogs/onsc_desempeno_dimension_views.xml',
        'views/catalogs/onsc_desempeno_skill_views.xml',
        'views/catalogs/onsc_desempeno_level_views.xml',
        'views/catalogs/onsc_desempeno_degree_views.xml',
        'views/catalogs/onsc_desempeno_degree_progress_views.xml',
        'views/catalogs/onsc_desempeno_development_means_views.xml',
        'views/catalogs/onsc_desempeno_reason_change_evaluator_views.xml',
        'views/onsc_desempeno_general_cycle_views.xml',
        'views/onsc_desempeno_settings_view.xml',
        'views/onsc_desempeno_evaluation_stage_views.xml',
        'views/onsc_desempeno_evaluation_list_views.xml',
        'views/onsc_desempeno_evaluation_views.xml',
        'views/onsc_desempeno_competency_views.xml',
        'views/onsc_desempeno_menuitems.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
