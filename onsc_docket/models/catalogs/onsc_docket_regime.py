# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCDocketRegime(models.Model):
    _name = 'onsc.docket.regime'
    _description = 'Regimen'

    codigo = fields.Char(string=u"Código")
    descripcion = fields.Char(string=u"Descripción")
    name = fields.Char(string="Nombre", compute='_compute_name', store=True)
    active = fields.Boolean(string="Activo", default=True)
    ind_vencimiento = fields.Boolean(string="IND_VENCIMIENTO")
    presupuesto = fields.Boolean(string="PRESUPUESTO")
    vigente = fields.Boolean(string="VIGENTE")

    @api.depends('codigo', 'descripcion')
    def _compute_name(self):
        for record in self:
            if record.codigo and record.descripcion:
                record.name = '%s - %s' % (record.codigo, record.descripcion)
            else:
                record.name = ''
