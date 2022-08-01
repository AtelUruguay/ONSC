# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = ['operating.unit', 'model.history']
    _name = 'operating.unit'
    _history_model = 'operating.unit.history'

    name = fields.Char(required=True, history=True)
    code = fields.Char(required=True, history=True)
    active = fields.Boolean(default=True, history=True)
    partner_id = fields.Many2one("res.partner", "Partner", required=True, history=True)

    budget_code = fields.Char(u'Código presupuestal (SIIF)', required=True, history=True)
    date_begin = fields.Date(string='Inicio de vigencia', required=True, history=True)
    date_end = fields.Date(string='Fin de vigencia', history=True)
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

class OperatingUnitHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'operating.unit.history'
    _parent_model = 'operating.unit'
