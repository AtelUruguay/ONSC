# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoLegend(models.Model):
    _name = 'onsc.legajo.legend'
    _description = "Acto electoral"

    legend = fields.Char(string="Texto de leyenda", required=True)
    regime_id = fields.Many2one("onsc.legajo.regime", "Régimen")
    descriptor1_id = fields.Many2one("onsc.catalog.descriptor1", "Descriptor 1")
    active = fields.Boolean("Activo", default=True)

    @api.constrains("regime_id", "regime_id")
    def _check_regime_descriptor(self):
        Legend = self.env['onsc.legajo.legend'].suspend_security()

        for record in self:
            if not record.regime_id and not record.regime_id:
                raise ValidationError(_("Se debe ingresar Régimen y/o Descriptor 1"))
            if Legend.search_count([('regime_id', '=', record.regime_id.id), ('descriptor1_id', '=', record.descriptor1_id.id), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_("Ya existe una legenda para el Régimen y Descriptor 1 ingresado"))
