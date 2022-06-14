# -*- coding: utf-8 -*-

from odoo import models, api


class ResUsers(models.Model):
    """Adiciona info de Id Digita la creacion del Partner"""
    _inherit = 'res.users'

    @api.model
    def _prepare_userinfo_dict(self, provider, params):
        result = super(ResUsers, self)._prepare_userinfo_dict(provider, params)
        result.update({
        })
        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        values['name'] = values.get('name', '').upper()
        return super(ResPartner, self).create(values)

    def write(self, values):
        return super(ResPartner, self).write(values)
