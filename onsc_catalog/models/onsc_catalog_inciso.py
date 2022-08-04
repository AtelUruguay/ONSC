# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api


class ONSCCatalogInciso(models.Model):
    _name = 'onsc.catalog.inciso'
    _inherits = {'res.company': 'company_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Incisos'

    company_id = fields.Many2one('res.company',
                                 required=True,
                                 auto_join=True,
                                 index=True,
                                 ondelete="cascade")
    identifier = fields.Char(string="Identificador", required=True, tracking=True)
    budget_code = fields.Char(u"Código presupuestal (SIIF)", required=True, tracking=True)
    short_name = fields.Char("Sigla", required=True, tracking=True)
    date_begin = fields.Date(string="Inicio de vigencia", required=True, tracking=True)
    date_end = fields.Date(string="Fin de vigencia", tracking=True)
    createupdate_regulation = fields.Char(u"Normativa de creación/modificación", tracking=True)
    description = fields.Text('Observaciones')
    active = fields.Boolean(string="Activo", default=True, tracking=True)
    is_institutional = fields.Boolean(u"¿Es institucional?", tracking=True)
    is_public_company = fields.Boolean(u"¿Es empresa pública?", tracking=True)
    is_into_nacional_budget = fields.Boolean(u"¿Integra el presupuesto nacional?", tracking=True)
    section_220_221 = fields.Char(u"Artículo 220 o 221", tracking=True)
    reference_ministry = fields.Char("Ministerio de referencia", tracking=True)
    is_central_administration = fields.Boolean(u"¿Es administración central?", tracking=True)

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime("Fecha de última modificación", index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    _sql_constraints = [
        ('identifier_uniq', 'unique(identifier)', u'El identificador debe ser único'),
        ('budget_code_uniq', 'unique(budget_code)', u'El código presupuestal (SIIF) ser único'),
        ('short_name_uniq', 'unique(short_name)', u'La sigla debe ser única'),
    ]


class ONSCCatalogIncisoView(models.Model):
    _name = 'onsc.catalog.inciso.report'
    _description = 'Vista sql de incisos'
    _auto = False

    identifier = fields.Char('Identificador')
    company_id = fields.Integer('Id de compañía')
    name = fields.Char('Nombre', compute='_compute_name', compute_sudo=True)
    budget_code = fields.Char('Código presupuestal (SIIF)')
    short_name = fields.Char('Sigla')
    date_begin = fields.Date(string="Inicio de vigencia")
    date_end = fields.Date(string="Fin de vigencia")

    @api.depends('company_id')
    def _compute_name(self):
        for rec in self:
            rec.name = self.env['res.company'].browse(rec.company_id).name

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
              CREATE OR REPLACE VIEW %s AS (
              SELECT id, identifier, company_id, budget_code, short_name, date_begin, date_end
                FROM onsc_catalog_inciso)''' % (self._table,))
