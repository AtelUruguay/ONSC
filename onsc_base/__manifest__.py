# -*- coding: utf-8 -*-
{
    'name': 'ONSC - Base',
    'version': '15.0.28.0.0',
    'summary': 'ONSC - Base',
    'sequence': 11,
    'description': """
ONSC - Base
====================
    """,
    'category': 'ONSC',
    'depends': [
        'base',
        'mail',
        'web_responsive',
        'website',
        'auth_iduy_primary_login',
        'base_user_role',
        'web_edit_button_conditional_disable',
        'mail_outbound_static',
        'mail_outbound_static_fixed',
        'auth_session_timeout_clean',
        'fields_many2one_restrict',
        'base_restrict_access',
        'url_access_restriction',
        'disable_userprofile_menuitems',
        'field_binary_show_filename'
    ],
    'data': [
        'security/onsc_base_security.xml',
        'security/ir.model.access.csv',
        'data/res_user_role_data.xml',
        'wizard/onsc_confirm_wizard_views.xml',
        'views/onsc_log_views.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
