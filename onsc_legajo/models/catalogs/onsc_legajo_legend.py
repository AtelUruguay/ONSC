# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoLegend(models.Model):
    _name = 'onsc.legajo.legend'
    _description = "Leyenda Ley 19574-380-2018"

    name = fields.Char(string="Texto de leyenda", required=True)
    regime_id = fields.Many2one("onsc.legajo.regime", "Régimen")
    descriptor1_id = fields.Many2one("onsc.catalog.descriptor1", "Descriptor 1")
    active = fields.Boolean("Activo", default=True)

    def _get_legajo_legend(self, regime_id, descriptor1_id):
        """

        :param regime_id: Id of Regimen record
        :param descriptor1_id: Id of Descriptor1 record
        """
        result_record = False
        for rec in self.sudo().search([]):
            match_regime = rec.regime_id.id == regime_id
            match_descriptor1 = rec.descriptor1_id.id == descriptor1_id
            if regime_id and match_regime and descriptor1_id and match_descriptor1:
                result_record = rec
            elif regime_id and match_regime and not descriptor1_id and not result_record:
                result_record = rec
            elif descriptor1_id and match_descriptor1 and not result_record:
                result_record = rec
        return result_record



    @api.constrains("regime_id", "descriptor1_id")
    def _check_regime_descriptor(self):
        Legend = self.env['onsc.legajo.legend'].suspend_security()
        for record in self:
            if not record.descriptor1_id and not record.regime_id:
                raise ValidationError(_("Se debe ingresar Régimen y/o Descriptor 1"))
            if Legend.search_count([
                ('regime_id', '=', record.regime_id.id),
                ('descriptor1_id', '=', record.descriptor1_id.id),
                ('id', '!=', record.id)]) > 0:
                raise ValidationError(_("Ya existe una Leyenda para el Régimen y Descriptor 1 ingresado"))
