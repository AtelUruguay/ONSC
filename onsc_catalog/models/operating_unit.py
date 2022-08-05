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
    partner_id = fields.Many2one("res.partner", "Partner", required=True, history=True)

    budget_code = fields.Char(u'Código presupuestal (SIIF)', required=True, history=True)
    start_date = fields.Date(string='Inicio de vigencia', required=True, history=True)
    end_date = fields.Date(string='Fin de vigencia', history=True)
    createupdate_regulation = fields.Char(u'Normativa de creación/modificación', tracking=True, history=True)
    description = fields.Text('Observaciones', history=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True, history=True)
    company_id = fields.Many2one('res.company',
                                 related='inciso_id.company_id',
                                 store=True, history=True)

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime('Fecha de última modificación', index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    _sql_constraints = [
        ('budget_code_uniq', 'unique(budget_code)', u'El código presupuestal (SIIF) ser único'),
        ('short_name_uniq', 'unique(short_name)', u'La sigla debe ser única'),
    ]

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.partner_id = self.company_id.partner_id

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

    name = fields.Char('Nombre', compute='_compute_fields_with_history', compute_sudo=True)
    short_name = fields.Char('Sigla', compute='_compute_fields_with_history', compute_sudo=True)
    code = fields.Char('Código', compute='_compute_fields_with_history', compute_sudo=True)
    budget_code = fields.Char(u"Código presupuestal (SIIF)", compute='_compute_fields_with_history', compute_sudo=True)
    start_date = fields.Date(string="Inicio de vigencia")
    end_date = fields.Date(string="Fin de vigencia")
    company_id = fields.Integer('Id de compañía')
    inciso_id = fields.Integer('Inciso', compute='_compute_fields_with_history', compute_sudo=True)
    inciso_report_id = fields.Many2one('onsc.catalog.inciso.report', 'Inciso', compute='_compute_inciso_report_id',
                                       search='_search_inciso_report_id')

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
            rec.inciso_id = read_values.get('inciso_id') and read_values.get('inciso_id')[0] or 0

    def _search_inciso_report_id(self, operator, value):
        return [('inciso_id', operator, value)]

    @api.depends('inciso_id')
    def _compute_inciso_report_id(self):
        for rec in self:
            rec.inciso_report_id = self.env['onsc.catalog.inciso.report'].browse(rec.inciso_id)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
              CREATE OR REPLACE VIEW %s AS (
              SELECT id, start_date, end_date, company_id FROM operating_unit)''' % (self._table,))
