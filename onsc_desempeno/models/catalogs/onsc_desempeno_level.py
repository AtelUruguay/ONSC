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

    @api.constrains('level_line_ids')
    def _check_level_line_ids(self):

        for record in self:
            if len(record.level_line_ids) == 0:
                raise ValidationError(_(u"Se debe tener 1 línea configurada"))

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
    active = fields.Boolean(string="Activo", related='level_id.active', store=True)

    _sql_constraints = [
        ('level_line_uniq', 'unique(hierarchical_level_id,is_uo_manager)',
         u'La combinación de nivel jerárquico y responsable UO solo puede estar asociada a un nivel'),
    ]

