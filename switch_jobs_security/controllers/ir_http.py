# -*- coding: utf-8 -*-
# flake8: noqa: R8180
from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.http import request


class Http(Home):
    _inherit = 'ir.http'

    @http.route()
    def web_login(self, *args, **kw):
        if 'login' in kw:
            obj_user = request.env['res.users'].sudo().search([('login', '=', kw['login'])])
            if obj_user:
                domain = [('employee_id', '=', obj_user.employee_id.id)]
                jobs = request.env['hr.job'].sudo().search(domain)
                if jobs:
                    obj_user.reset_roles()
        res = super(Http, self).web_login(*args, **kw)
        return res
