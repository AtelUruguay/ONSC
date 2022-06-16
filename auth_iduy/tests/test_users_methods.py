# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class TestUserMethods(common.TransactionCase):

    def setUp(self):
        """setup base method"""
        super(TestUserMethods, self).setUp()

    def test_00_auth_oauth(self):
        """"""
        provider = self.env.ref('auth_iduyauth_oauth.auth_openid_iduy')
        result = self.env['res.users'].auth_oauth(provider, {
            'email': 'admin',
            'access_token': 'access_token'
        })
        self.assertIsNone(result)
