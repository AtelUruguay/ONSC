# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    budget_code = fields.Char(u"Código presupuestal (SIIF)", required=True)
    date_begin = fields.Date(string="Inicio de vigencia", required=True)
    date_end = fields.Date(string="Fin de vigencia")
    createupdate_regulation = fields.Char(u"Normativa de creación/modificación", tracking=True)
    description = fields.Text('Observaciones')
    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso", required=True)
    company_id = fields.Many2one("res.company",
                                 related='inciso_id.company_id',
                                 store=True)

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime("Fecha de última modificación", index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    _sql_constraints = [
        ('budget_code_uniq', 'unique(budget_code)', u'El código presupuestal (SIIF) ser único'),
        ('short_name_uniq', 'unique(short_name)', u'La sigla debe ser única'),
    ]

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.partner_id = self.company_id.partner_id


class OperatingUnitReport(models.Model):
    _name = 'operating.unit.report'
    _description = 'Vista sql de unidad operativa'
    _auto = False

    name = fields.Char('Nombre')
    code = fields.Char('Código')
    budget_code = fields.Char(u"Código presupuestal (SIIF)")
    date_begin = fields.Date(string="Inicio de vigencia")
    date_end = fields.Date(string="Fin de vigencia")
    company_id = fields.Integer('Id de compañía')
    inciso_id = fields.Integer('Inciso')
    inciso_report_id = fields.Many2one('onsc.catalog.inciso.report', 'Inciso', compute='compute_inciso_report_id',
                                       search='_search_inciso_report_id')

    def _search_inciso_report_id(self, operator, value):
        return [('inciso_id', operator, value)]

    @api.depends('inciso_id')
    def compute_inciso_report_id(self):
        for rec in self:
            rec.inciso_report_id = self.env['onsc.catalog.inciso.report'].browse(rec.inciso_id)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
              CREATE OR REPLACE VIEW %s AS (
              SELECT id, code, name, budget_code, date_begin, date_end, company_id, inciso_id
                FROM operating_unit)''' % (self._table,))
