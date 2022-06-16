# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class AuthOauthProvider(models.Model):
    """"""
    _inherit = 'auth.oauth.provider'

    redirect_uri = fields.Char(string="Redirect URI", required=False, )
    secret_key = fields.Char(string="Secret Key", required=False, )

    flow = fields.Selection([
        ('access_token', 'OAuth2'),
        ('id_uy', 'Id Uruguayo')
    ],
        string='OAuth Flow',
        required=True,
        default='access_token')
