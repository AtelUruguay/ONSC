# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoOffice(models.Model):
    _name = 'onsc.legajo.office'
    _description = 'Oficina'


    inciso = fields.Many2one(comodel_name="onsc.catalog.inciso", string="Inciso")
    unidadEjecutora = fields.Many2one(comodel_name="operating.unit", string="Unidad ejecutora")


    active = fields.Boolean(string="Activo", default=True)

    def syncronize(self):
        return True
