# -*- coding: utf-8 -*-

from odoo import models, _


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    def fields_get(self, allfields=None, attributes=None):
        res = super(ResCountryState, self).fields_get(allfields, attributes)
        # Inherit to fix labels
        res = self._apply_fix_label(res)
        return res

    def _apply_fix_label(self, res):
        for field in res:
            if field == 'name':
                res[field]['string'] = _('Nombre del Departamento')
            if field == 'code':
                res[field]['string'] = _('Código del Departamento')
                res[field]['help'] = _('Código del Departamento')
        return res
