# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCLegajoRegime(models.Model):
    _name = 'onsc.legajo.regime'
    _description = 'Régimen'

    codigo = fields.Char(string=u"Código", required=True)
    descripcion = fields.Char(string=u"Descripción", required=True)
    name = fields.Char(string="Nombre", compute='_compute_name', store=True)
    ind_vencimiento = fields.Boolean(string="Ind Vencimiento")
    presupuesto = fields.Boolean(string="Presupuesto")
    vigente = fields.Boolean(string="Vigente")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('codigo_uniq', 'unique(codigo)', u'El código del régimen debe ser único'),
        ('descripcion_uniq', 'unique(descripcion)', u'La descripción del régimen debe ser única')
    ]

    def syncronize(self):
        return True

    @api.depends('codigo', 'descripcion')
    def _compute_name(self):
        for record in self:
            if record.codigo and record.descripcion:
                record.name = '%s - %s' % (record.codigo, record.descripcion)
            else:
                record.name = ''
