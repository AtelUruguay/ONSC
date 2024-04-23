# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.addons import base
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)


base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')


class ResUsers(models.Model):
    """"""
    _inherit = 'res.users'

    @api.model
    def auth_oauth(self, provider, params):
        """
        Adiciona alternativa IdUy
        @rtype: object
        """
        if provider.flow == 'id_uy':
            return self.auth_iduy_oauth(provider, params)
        else:
            return super(ResUsers, self).auth_oauth(provider, params)

    @api.model
    def auth_iduy_oauth(self, provider, params):
        """
        siging propio de IdUY
        @rtype: object
        """
        user = self._auth_iduy_signin(provider.id, params)
        return (self.env.cr.dbname, user.login, user.oauth_access_token)

    @api.model
    def _prepare_userinfo_dict(self, provider, params):
        result = {
            'login': params.get('email', ''),
            'email': params.get('email', ''),
            'name': params.get('name', ''),
            'oauth_uid': params.get('uid', False),
            'oauth_access_token': params.get('access_token'),
            'vat': params.get('numero_documento', False),
            'oauth_provider_id': provider,

        }
        country = self._get_country_code(params)
        if country:
            result['country_id'] = country.id
        return result

    @api.model
    def _get_user(self, provider, params):
        self._check_valid_login(provider, params)
        if params.get('uid', False):
            args = [("oauth_uid", "=", params.get('uid'))]
        else:
            args = [("login", "=", params.get('email'))]
        args.append(('oauth_provider_id', '=', provider))
        oauth_user = self.search(args)
        userinfo_dict = self._prepare_userinfo_dict(provider, params)
        if not oauth_user:
            return self.sudo().with_context(is_new_user=True).create(userinfo_dict)
        else:
            oauth_user.sudo().write(userinfo_dict)
            return oauth_user

    @api.model
    def _check_valid_login(self, provider, params):
        """
        No se permite que mas de un usuario tenga el mismo login, usando como llave complementario el oauth_uid
        :param provider:
        :param params:
        """
        _logger.info('IDUY: Check user login**************')
        if params.get('uid', False) and params.get('email'):
            args = [
                ("login", "=", params.get('email')),
                ('oauth_provider_id', '=', provider),
                ('oauth_uid', '!=', params.get('uid', False))
            ]
            if self.sudo().search_count(args):
                _logger.info('IDUY:IS USER WITH OTHER LOGIN IN SYSTEM**************')
                raise Exception(_("IDUY: BAD USER LOGIN"))

    @api.model
    def _auth_iduy_signin(self, provider, params):
        """
        Se guarda en el usuario el access_token con el fin de usarlo como contrasena
        @rtype: res.user identificado y con su access_token actualizado
        """
        try:
            oauth_user = self._get_user(provider, params)
            assert len(oauth_user) == 1
            return oauth_user
        except AccessDenied:
            raise AccessDenied()

    def _get_country_code(self, params):
        """

        @rtype: object of country
        """
        _pais_documento = params.get('pais_documento', False)
        if _pais_documento and _pais_documento.get('codigo', False):
            country_code = _pais_documento.get('codigo', 'UY')

        return self.env['res.country'].search([
            ('code', 'in', [country_code.upper(), country_code.lower()])
        ], limit=1)
