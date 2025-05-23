# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Gestión de Desempeño',
    'version': '15.0.6.0.0',
    'summary': 'ONSC - Gestión de Desempeño',
    'sequence': 1,
    'description': """
ONSC - Gestión de Desempeño
====================
    """,
    'category': 'ONSC',
    'depends': [
        'mail',
        'model_history',
        'base_suspend_security',
        'onsc_base',
        'onsc_catalog',
        'onsc_legajo',
        'excel_import_export'
    ],
    "data": [
        "security/onsc_desempeno_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        "data/ir_evaluation_type_data.xml",
        "data/reason_data.xml",
        "wizard/onsc_user_notification_atlogin_views.xml",
        "wizard/onsc_desempeno_evaluator_change_wizard_views.xml",
        "wizard/onsc_desempeno_extend_deadline_views.xml",
        "wizard/onsc_desempeno_evaluator_cancel_wizard_views.xml",
        "wizard/onsc_desempeno_evaluation_report_wizard.xml",
        "wizard/onsc_desempeno_general_note_views.xml",
        "wizard/onsc_desempeno_brecha_wizard.xml",
        "reports_xlsx/report_onsc_desempeno_evaluation_report.xml",
        "reports_xlsx/templates.xml",
        "reports/report_onsc_desempeno_evaluation_report.xml",
        "views/catalogs/onsc_legajo_base_views.xml",
        "views/catalogs/onsc_desempeno_dimension_views.xml",
        "views/catalogs/onsc_desempeno_skill_views.xml",
        "views/catalogs/onsc_desempeno_level_views.xml",
        "views/catalogs/onsc_desempeno_degree_views.xml",
        "views/catalogs/onsc_desempeno_degree_progress_views.xml",
        "views/catalogs/onsc_desempeno_development_means_views.xml",
        "views/catalogs/onsc_desempeno_reason_change_evaluator_views.xml",
        "views/catalogs/onsc_desempeno_reason_cancellation_views.xml",
        "views/onsc_desempeno_score_views.xml",
        "views/onsc_desempeno_general_cycle_views.xml",
        "views/onsc_desempeno_settings_view.xml",
        "views/onsc_desempeno_evaluation_stage_views.xml",
        "views/onsc_desempeno_evaluation_list_views.xml",
        "views/onsc_desempeno_evaluation_views.xml",
        "views/onsc_desempeno_competency_views.xml",
        "views/onsc_desempeno_consolidated_views.xml",
        "views/onsc_desempeno_development_plan_views.xml",
        "views/onsc_desempeno_evaluation_summary_views.xml",
        "views/onsc_desempeno_evaluation_report_views.xml",
        "views/onsc_legajo_views_inherit.xml",
        "views/onsc_frequency_equivalence_views.xml",
        "views/onsc_desempeno_competency_skills_views.xml",
        "views/onsc_desempeno_menuitems.xml",
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
