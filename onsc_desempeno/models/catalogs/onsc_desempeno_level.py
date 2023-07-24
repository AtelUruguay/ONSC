# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoLevel(models.Model):
    _name = 'onsc.desempeno.level'
    _description = 'Niveles'

    name = fields.Char(string="Nombre del nivel", required=True)
    definition = fields.Char(string="Descripción")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del nivel debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoLevel, self).copy(default=default)
    def toggle_active(self):
        return super(ONSCDesempenoLevel, self.with_context(no_check_write=True)).toggle_active()


class ONSCCatalogOccupationDesempeno(models.Model):
    _inherit = ['onsc.catalog.occupation']
    _name = 'onsc.catalog.occupation'

    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel de requerimiento")
