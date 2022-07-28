# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    budget_code = fields.Char(u"Código presupuestal (SIIF)", required=True)
    date_begin = fields.Date(string="Inicio de vigencia", required=True)
    date_end = fields.Date(string="Fin de vigencia")
    createupdate_regulation = fields.Char(u"Normativa de creación/modificación", tracking=True)
    description = fields.Text('Observaciones')
    company_id = fields.Many2one(
        "res.company",
        required=True,
        readonly=False,
        default=lambda self: self.env.company,
    )

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

