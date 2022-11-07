{
    'name': 'ID Uruguay Primary Login',
    'version': '15.0.1.1.0.',
    'license': '',
    'author': "Quanam",
    'website': "https://www.quanam.com",
    'description': """
Allow users to login through Id Uruguay Connect Provider.
=====================================================
- Keycloak with ClientID and Secret + Implicit Flow

""",
    'depends': ['auth_iduy', 'auth_oauth', 'web'],
    'data': [
        'views/webclient_templates.xml',
        'views/auth_oauth_templates.xml',
    ],
}
