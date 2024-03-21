# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class ONSCLegajoTypeDemerit(models.Model):
    _name = 'onsc.legajo.type.demerit'
    _description = "Tipo de demérito"

    name = fields.Char("Tipo de demérito", required=True)
    active = fields.Boolean("Activo", default=True)

    _sql_constraints = [('name_uniq', 'UNIQUE (name)', _('Ya existe un Tipo de demérito con el mismo nombre'))]


class ONSCLegajoTypeSanction(models.Model):
    _name = 'onsc.legajo.type.sanction'
    _description = "Tipo de sanción"

    name = fields.Char("Tipo de sanción", required=True)
    demerit_id = fields.Many2one("onsc.legajo.type.demerit", 'Tipo de demérito', required=True)
    active = fields.Boolean("Activo", default=True)
    summary = fields.Text("Sumario")

    _sql_constraints = [('sanction_uniq', 'UNIQUE (name,demerit_id)',
                         _('Ya existe ese Tipo de sanción para ese Tipo de demérito'))]
