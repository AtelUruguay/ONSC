# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning


class OperatingUnit(models.Model):
    _inherit = ['operating.unit', 'model.history']
    _name = 'operating.unit'
    _history_model = 'operating.unit.history'

    name = fields.Char(required=True, history=True)
    short_name = fields.Char(string="Sigla", required=True, history=True)
    code = fields.Char(required=True, history=True)
    active = fields.Boolean(default=True, history=True)
    partner_id = fields.Many2one("res.partner", "Partner", related='company_id.partner_id',
                                 store=True,
                                 readonly=True,
                                 required=False,
                                 history=True)

    budget_code = fields.Char(u'Código presupuestal (SIIF)', required=True, history=True)
    start_date = fields.Date(string='Inicio de vigencia', required=True, history=True)
    end_date = fields.Date(string='Fin de vigencia', history=True)
    createupdate_regulation = fields.Char(u'Normativa de creación/modificación', tracking=True, history=True)
    description = fields.Text('Observaciones', history=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True, history=True)
    company_id = fields.Many2one('res.company',string="Compañia",
                                 related='inciso_id.company_id',
                                 store=True, history=True, ondelete='restrict')

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime('Fecha de última modificación', index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    _sql_constraints = [
        ('budget_code_uniq', 'unique (budget_code, inciso_id)',
         u'La combinación de inciso y el código presupuestal (SIIF) debe ser única'),
        ('short_name_uniq', 'unique(short_name,inciso_id)',
         u'La combinación de inciso y sigla debe ser única'),
        ("code_company_uniq", "unique (code)", "El código debe ser único!",),
        ("name_company_uniq", "unique (name,inciso_id)", "La combinación de inciso y nombre debe ser única",),
    ]

    def name_get(self):
        res = []
        for ou in self:
            res.append((ou.id, ou.name))
        return res

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return catalog_warning(_(u"La fecha de inicio de vigencia no puede ser mayor "
                                     u"que la fecha de fin de vigencia"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return catalog_warning(_(u"La fecha de fin de vigencia no puede ser menor "
                                     u"que la fecha de inicio de vigencia"))


class OperatingUnitHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'operating.unit.history'
    _parent_model = 'operating.unit'


class OperatingUnitReport(models.Model):
    _name = 'operating.unit.report'
    _description = 'Vista sql de unidad operativa'
    _auto = False

    name = fields.Char('Nombre', compute='_compute_fields_with_history', compute_sudo=True, search='_search_name_ou')
    short_name = fields.Char('Sigla', compute='_compute_fields_with_history', compute_sudo=True,
                             search='_search_short_name')
    code = fields.Char('Código', compute='_compute_fields_with_history', compute_sudo=True, search='_search_code')
    budget_code = fields.Char(u"Código presupuestal (SIIF)", compute='_compute_fields_with_history', compute_sudo=True,
                              search='_search_budget_code')
    start_date = fields.Date(string="Inicio de vigencia")
    end_date = fields.Date(string="Fin de vigencia")
    company_id = fields.Integer('Id de compañía')
    inciso_id = fields.Integer('Inciso', compute='_compute_fields_with_history', search='_search_inciso_id',
                               compute_sudo=True)

    @api.depends('company_id')
    def _compute_fields_with_history(self):
        for rec in self:
            OU = self.env['operating.unit'].browse(rec.id).read(['name', 'short_name', 'code',
                                                                 'budget_code', 'inciso_id'])
            read_values = OU and OU[0] or {}

            rec.name = read_values.get('name')
            rec.short_name = read_values.get('short_name')
            rec.code = read_values.get('code')
            rec.budget_code = read_values.get('budget_code')
            inciso_id = read_values.get('inciso_id')
            inciso_id = isinstance(inciso_id, tuple) and inciso_id[0]
            rec.inciso_id = inciso_id

    def _search_inciso_id(self, operator, value):
        OU = self.env['operating.unit'].sudo().search([('inciso_id', operator, value)])
        return [('id', 'in', OU.ids)]

    def _search_name_ou(self, operator, value):
        OU = self.env['operating.unit'].sudo().search([('name', operator, value)])
        return [('id', 'in', OU.ids)]

    def _search_short_name(self, operator, value):
        OU = self.env['operating.unit'].sudo().search([('short_name', operator, value)])
        return [('id', 'in', OU.ids)]

    def _search_code(self, operator, value):
        OU = self.env['operating.unit'].sudo().search([('code', operator, value)])
        return [('id', 'in', OU.ids)]

    def _search_budget_code(self, operator, value):
        OU = self.env['operating.unit'].sudo().search([('budget_code', operator, value)])
        return [('id', 'in', OU.ids)]

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
              CREATE OR REPLACE VIEW %s AS (
              SELECT id, start_date, end_date, company_id FROM operating_unit)''' % (self._table,))
