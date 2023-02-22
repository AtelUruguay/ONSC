# -*- coding: utf-8 -*-
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo import http


class Http(Home):
    _inherit = 'ir.http'

    @http.route()
    def web_login(self, *args, **kw):
        res = super(Http, self).web_login(*args, **kw)
        if 'login' in kw:
            obj_user = request.env['res.users'].sudo().search([('login', '=', kw['login'])])
            obj_user.reset_roles()
        return res
