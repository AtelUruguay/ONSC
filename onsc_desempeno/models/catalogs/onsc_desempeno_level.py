# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoLevel(models.Model):
    _name = 'onsc.desempeno.level'
    _description = 'Niveles'

    name = fields.Char(string="Nombre del nivel", required=True)
    definition = fields.Text(string="Descripción")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del nivel debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoLevel, self).copy(default=default)


class ONSCCatalogOccupation(models.Model):
    _inherit = 'onsc.catalog.occupation'

    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel de requerimiento")
