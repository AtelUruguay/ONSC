# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as catalog_warning


class ONSCCatalogInciso(models.Model):
    _name = 'onsc.catalog.inciso'
    _inherits = {'res.company': 'company_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin', 'model.history']
    _description = 'Incisos'
    _history_model = 'onsc.catalog.inciso.history'

    company_id = fields.Many2one('res.company',
                                 required=True,
                                 auto_join=True,
                                 index=True,
                                 ondelete="cascade")
    company_name = fields.Char(related='company_id.name',
                               string='Nombre',
                               store=True,
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
    is_central_administration = fields.Boolean(u"¿Es administración central?", tracking=True, history=True)

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


class ONSCCatalogIncisoHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.catalog.inciso.history'
    _parent_model = 'onsc.catalog.inciso'
