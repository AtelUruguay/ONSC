# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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
    identifier = fields.Integer(string="Identificador", required=True)
    budget_code = fields.Char(u"Código presupuestal (SIIF)", required=True)
    short_name = fields.Char("Sigla", required=True)
    date_begin = fields.Date(string="Inicio de vigencia", required=True)
    date_end = fields.Date(string="Fin de vigencia")
    createupdate_regulation = fields.Char(u"Normativa de creación/modificación")
    description = fields.Text('Observaciones')
    active = fields.Boolean(string="Activo", default=True)
    # TODO clasificaciones
    is_institutional = fields.Boolean(u"¿Es institucional?")
    is_public_company = fields.Boolean(u"¿Es empresa pública?")
    is_into_nacional_budget = fields.Boolean(u"¿Integra el presupuesto nacional?")
    section_220_221 = fields.Char(u"Artículo 220 o 221")
    reference_ministry = fields.Char("Ministerio de referencia", )
    is_central_administration = fields.Boolean(u"¿Es administración central?")

    create_date = fields.Date(string=u'Fecha de creación', index=True, readonly=True)
    write_date = fields.Datetime("Fecha de última modificación", index=True, readonly=True)
    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)
    write_uid = fields.Many2one('res.users', string='Actualizado por', index=True, readonly=True)

