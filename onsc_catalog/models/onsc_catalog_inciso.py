# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning


class ONSCCatalogInciso(models.Model):
    _name = 'onsc.catalog.inciso'
    _inherits = {'res.company': 'company_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin', 'model.history']
    _description = 'Incisos'
    _history_model = 'onsc.catalog.inciso.history'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        """
        if self.user_has_groups('onsc_catalog.group_catalog_configurador_servicio_civil'):
            args += [('company_id', 'in', self._context.get('allowed_company_ids'))]
        return super(ONSCCatalogInciso, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                      access_rights_uid=access_rights_uid)

    company_id = fields.Many2one('res.company',
                                 required=True,
                                 auto_join=True,
                                 index=True,
                                 ondelete="cascade")
    company_name = fields.Char(related='company_id.name',
                               string='Nombre',
                               readonly=False,
                               store=True,
                               tracking=True,
                               history=True)
    identifier = fields.Char(string="Identificador", required=True, tracking=True, history=True)
    budget_code = fields.Char(u"Código presupuestal (SIIF)", required=True, tracking=True, history=True)
    short_name = fields.Char("Sigla", required=True, tracking=True, history=True)
    start_date = fields.Date(string="Inicio de vigencia", required=True, tracking=True, history=True)
    end_date = fields.Date(string="Fin de vigencia", tracking=True, history=True)
    createupdate_regulation = fields.Char(u"Normativa de creación/modificación", tracking=True, history=True)
    description = fields.Text('Observaciones', history=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True, history=True)
    is_institutional = fields.Boolean(u"¿Es institucional?", tracking=True, history=True)
    is_public_company = fields.Boolean(u"¿Es empresa pública?", tracking=True, history=True)
    is_into_nacional_budget = fields.Boolean(u"¿Integra el presupuesto nacional?", tracking=True, history=True)
    section_220_221 = fields.Char(u"Artículo 220 o 221", tracking=True, history=True)
    reference_ministry = fields.Char("Ministerio de referencia", tracking=True, history=True)
    is_central_administration = fields.Boolean(u"¿Es administración central?",
                                               tracking=True,
                                               history=True,
                                               default=True)

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime("Fecha de última modificación", index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

    _sql_constraints = [
        ('identifier_uniq', 'unique(identifier)', u'El identificador debe ser único'),
        ('budget_code_uniq', 'unique(budget_code)', u'El código presupuestal (SIIF) ser único'),
        ('short_name_uniq', 'unique(short_name)', u'La sigla debe ser única'),
    ]

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

    @api.model
    def create(self, values):
        result = super(ONSCCatalogInciso, self).create(values)
        self.env.user.sudo().write({
            'company_ids': [(4, result.company_id.id)]
        })
        return result


class ONSCCatalogIncisoHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.catalog.inciso.history'
    _parent_model = 'onsc.catalog.inciso'


class ONSCCatalogIncisoView(models.Model):
    _name = 'onsc.catalog.inciso.report'
    _description = 'Vista sql de incisos'
    _auto = False

    identifier = fields.Char('Identificador', compute='_compute_fields_with_history', compute_sudo=True)
    company_id = fields.Integer('Id de compañía')
    name = fields.Char('Nombre', compute='_compute_fields_with_history', compute_sudo=True)
    budget_code = fields.Char('Código presupuestal (SIIF)', compute='_compute_fields_with_history', compute_sudo=True)
    short_name = fields.Char('Sigla', compute='_compute_fields_with_history', compute_sudo=True)
    start_date = fields.Date(string="Inicio de vigencia")
    end_date = fields.Date(string="Fin de vigencia")

    @api.depends('company_id')
    def _compute_fields_with_history(self):
        for rec in self:
            Inciso = self.env['onsc.catalog.inciso'].browse(rec.id).read(
                ['identifier', 'company_name', 'company_id', 'budget_code', 'short_name'])
            read_values = Inciso and Inciso[0] or {}

            rec.identifier = read_values.get('identifier')
            rec.name = read_values.get('company_name')
            rec.budget_code = read_values.get('budget_code')
            rec.short_name = read_values.get('short_name')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
              CREATE OR REPLACE VIEW %s AS (
              SELECT id, start_date, end_date, company_id FROM onsc_catalog_inciso)''' % (self._table,))
