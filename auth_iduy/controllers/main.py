# pylint: disable=E8102
import base64
import functools
import json
import logging

import requests
import werkzeug.urls
import werkzeug.utils
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo.addons.web.controllers.main import set_cookie_and_redirect, login_and_redirect
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo import registry as registry_get
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)

EXCEPTIONS_MSG = {
    'access_denied': 'IdUY: access denied, redirect to main page in case '
                     'a valid session exists, without setting cookies',
    'auth_signup': 'auth_signup not installed on DB %s: oauth sign up cancelled.'
}


def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)

    return wrapper


class OpenIDLogin(OAuthLogin):
    """ OPEN ID LOGIN"""

    def list_providers(self):
        """
        Lista de Proveedores, ajustes para compatiblidad con Id UY
        @return: lista de instancias
        """
        providers = super(OpenIDLogin, self).list_providers()
        for provider in providers:
            if provider.get('flow') == 'id_uy':
                params = werkzeug.urls.url_decode(provider['auth_link'].split('?')[-1])
                params.pop('response_type')
                redirect_uri = provider.get('redirect_uri', False) or params.get(
                    'redirect_uri')
                params['response_type'] = 'code'
                params['redirect_uri'] = redirect_uri
                provider['auth_link'] = "%s?%s" % (
                    provider['auth_endpoint'], werkzeug.urls.url_encode(params))
        return providers


class OAuthController(http.Controller):

    @api.model
    def _get_token_req(self, provider, kw):
        data = {
            'grant_type': 'authorization_code',
            'code': kw.get('code'),
            'redirect_uri': provider.redirect_uri,
        }

        authorization = base64.encodestring(
            ("%s:%s" % (provider.client_id, provider.secret_key)).encode())
        authorization = 'Basic %s' % authorization.decode().replace('\n', '')

        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'Authorization': authorization,
        }

        return requests.post(
            provider.validation_endpoint,
            data=data,
            headers=headers,
            verify=False)

    def _get_userinfo(self, provider, access_token):
        headers = {
            'Authorization': 'Bearer %s' % (access_token),
        }
        userinfo_req = requests.get(
            provider.data_endpoint,
            headers=headers,
            verify=False)
        return userinfo_req

    @http.route('/auth_oauth/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, **kw):
        """
        User sigin controller
        @type kw: object
        """
        state = json.loads(kw['state'])
        dbname = state['d']
        if not http.db_filter([dbname]):
            return BadRequest()
        provider = state['p']
        context = state.get('c', {})
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, context)

                provider = env['auth.oauth.provider'].browse(provider)

                token_req = self._get_token_req(provider, kw)
                if token_req.status_code != 200:
                    raise Exception
                token_resp_content_dict = eval(token_req.content.decode())

                access_token = token_resp_content_dict.get('access_token', 'empty')
                kw.update({
                    'access_token': access_token
                })

                userinfo_req = self._get_userinfo(provider, access_token)
                if userinfo_req.status_code != 200:
                    raise Exception
                userinfo_content_dict = eval(
                    userinfo_req.content.decode().replace('true', 'True'))
                kw.update(userinfo_content_dict)

                credentials = env['res.users'].sudo().auth_oauth(provider, kw)
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                redirect = werkzeug.url_unquote_plus(state['r']) if state.get(
                    'r') else False
                url = '/web'
                if redirect:
                    url = redirect
                elif action:
                    url = '/web#action=%s' % action
                elif menu:
                    url = '/web#menu_id=%s' % menu
                resp = login_and_redirect(*credentials, redirect_url=url)
                # Since /web is hardcoded, verify user has right to land on it
                group_user = request.env.user.has_group('base.group_user')
                if werkzeug.urls.url_parse(
                        resp.location).path == '/web' and not group_user:
                    resp.location = '/'
                return resp
            except AttributeError:
                # auth_signup is not installed
                _logger.error(
                    _(EXCEPTIONS_MSG.get('auth_signup')) % (
                        dbname,))
                url = "/web/login?oauth_error=1"
            except AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info(_(EXCEPTIONS_MSG.get('access_denied')))
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("IdUY: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)
