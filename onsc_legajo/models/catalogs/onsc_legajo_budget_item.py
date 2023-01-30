# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoBudgetItem(models.Model):
    _name = 'onsc.legajo.budget.item'
    _description = 'Partida'

    codPartida = fields.Char(string="Código de partida", required=True)
    dsc1Id = fields.Many2one("onsc.catalog.descriptor1", string="Descriptor 1")
    dsc2Id = fields.Many2one("onsc.catalog.descriptor2", string="Descriptor 2")
    dsc3Id = fields.Many2one("onsc.catalog.descriptor3", string="Descriptor 3", required=True)
    dsc4Id = fields.Many2one("onsc.catalog.descriptor4", string="Descriptor 4")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('code_uniq', 'unique("codPartida")', u'El código de la partida debe ser único'),
    ]

    def syncronize(self):
        return True
