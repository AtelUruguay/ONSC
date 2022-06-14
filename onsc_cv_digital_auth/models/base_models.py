# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ResUsers(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.users'

    @api.model
    def _prepare_userinfo_dict(self, provider, params):
        result = super(ResUsers, self)._prepare_userinfo_dict(provider, params)
        result.update({
        })
        return result


class ResPartner(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.partner'

    cv_dnic_name_1 = fields.Char(u'Primer nombre CI')
    cv_dnic_name_2 = fields.Char(u'Segundo nombre CI')
    cv_dnic_lastname_1 = fields.Char(u'Primer apellido CI')
    cv_dnic_lastname_2 = fields.Char(u'Segundo apellido CI')
    cv_last_name_adoptive_1 = fields.Char(u'Primer apellido adoptivo')
    cv_last_name_adoptive_2 = fields.Char(u'Segundo apellido adoptivo')
