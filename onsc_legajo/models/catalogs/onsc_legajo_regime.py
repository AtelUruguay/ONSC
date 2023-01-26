# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCLegajoRegime(models.Model):
    _name = 'onsc.legajo.regime'
    _description = 'Régimen'

    codigo = fields.Char(string=u"Código régimen", required=True)
    descripcion = fields.Char(string=u"Descripción régimen", required=True)
    name = fields.Char(string="Nombre del régimen", compute='_compute_name', store=True)
    ind_vencimiento = fields.Boolean(string="Requiere indicar fecha de vencimiento")
    presupuesto = fields.Boolean(string="Presupuesto")
    vigente = fields.Boolean(string="Vigente")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('codigo_uniq', 'unique(codigo)', u'El código de régimen debe ser único'),
        ('descripcion_uniq', 'unique(descripcion)', u'La descripción de régimen debe ser única')
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
