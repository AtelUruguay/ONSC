# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class ResCountry(models.Model):
    _inherit = 'res.country'

    def name_get(self):
        if self._context.get('format_phone_code'):
            result = []
            for country in self:
                name = '(%s) +%s' % (country.code, country.phone_code)
                result.append((country.id, name))
            return result
        return super(ResCountry, self).name_get()

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name and self._context.get('format_phone_code'):
            name = str(name)
            domain = [('phone_code', operator, name.split(' ')[0])]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    active = fields.Boolean(string="Activo", default=True)

    def fields_get(self, allfields=None, attributes=None):
        res = super(ResCountryState, self).fields_get(allfields, attributes)
        # Inherit to fix labels
        res = self._apply_fix_label(res)
        return res

    def _apply_fix_label(self, res):
        for field in res:
            if field == 'name':
                res[field]['string'] = _('Nombre del departamento')
            if field == 'code':
                res[field]['string'] = _('Código del departamento')
                res[field]['help'] = _('Código del departamento')
        return res
