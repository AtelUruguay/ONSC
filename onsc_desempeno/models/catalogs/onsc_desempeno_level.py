# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoLevel(models.Model):
    _name = 'onsc.desempeno.level'
    _description = 'Niveles'

    name = fields.Char(string="Nombre del nivel", required=True)
    definition = fields.Text(string="Descripción")
    active = fields.Boolean(string="Activo", default=True)
    level_line_ids = fields.One2many('onsc.desempeno.level.line', 'level_id', string='Lineas de Nivel')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre del nivel debe ser único'),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoLevel, self).copy(default=default)


class ONSCDesempenoLevelLine(models.Model):
    _name = 'onsc.desempeno.level.line'
    _description = 'Linea Niveles'

    level_id = fields.Many2one("onsc.desempeno.level", string="Nivel")
    hierarchical_level_id = fields.Many2one("onsc.catalog.hierarchical.level", string="Nivel jerárquico", required=True)
    is_uo_manager = fields.Boolean(string="Responsable UO", default=False)

    @api.constrains('hierarchical_level_id')
    def _check_unique_level(self):
        for record in self:
            if self.search_count([("hierarchical_level_id", "=", record.hierarchical_level_id.id),
                                  ("is_uo_manager", "=", record.is_uo_manager), ("id", "!=", record.id)]) > 0:
                raise ValidationError(_(u"Solo se puede tener un nivel jerarquico asociado a los niveles"))


class ONSCCatalogOccupation(models.Model):
    _inherit = 'onsc.catalog.occupation'

    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel de requerimiento")
