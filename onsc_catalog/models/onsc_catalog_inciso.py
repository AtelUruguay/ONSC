# -*- coding: utf-8 -*-

from odoo import models, fields


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
    identifier = fields.Integer(string="Identificador", required=True, tracking=True)
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
