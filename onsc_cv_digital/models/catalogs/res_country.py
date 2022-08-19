# -*- coding: utf-8 -*-

from odoo import models, fields, tools, _

class ResCountry(models.Model):
    _inherit = 'res.country'

    code_rve = fields.Char(string="Código RVE")

class ResCountryPhone(models.Model):
    _name = 'res.country.phone'
    _description = 'Prefijos telefónicos'
    _auto = False

    country_id = fields.Many2one('res.country', 'País')
    prefix_code = fields.Integer(related='country_id.phone_code', string='Código')
    name = fields.Char(compute='_compute_name', search='_search_name', string='Prefijo')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
              CREATE OR REPLACE VIEW %s AS (
              SELECT id, id as country_id FROM res_country)''' % (self._table,))

    def _compute_name(self):
        for rec in self:
            rec.name = '+%s' % rec.prefix_code

    def _search_name(self, operator, value):
        return ['|', '|', ('country_id.phone_code', operator, value), ('country_id', operator, value),
                ('country_id.code', operator, value)]


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
