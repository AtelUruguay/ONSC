{
    'name': 'Authentication IdUY Connect',
    'version': '1.0',
    'license': '',
    'author': "Quanam",
    'website': "https://www.quanam.com",
    'description': """
Allow users to login through Id Uruguay Connect Provider.
=====================================================
- Keycloak with ClientID and Secret + Implicit Flow

""",
    'depends': ['auth_oauth', 'auth_signup'],
    'data': [
        'data/auth_iduy_data.xml',
        'views/auth_oauth_provider.xml',
        'views/res_users.xml',
    ],
}
