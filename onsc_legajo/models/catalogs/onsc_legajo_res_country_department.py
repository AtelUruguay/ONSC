# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCLegajoCountryDepartment(models.Model):
    _name = 'onsc.legajo.res.country.department'
    _description = "Departamento donde desempeña funciones"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)
    active = fields.Boolean("Activo", default=True)
    state_id = fields.Many2one('res.country.state', string='Departamento',
                               domain="[('country_id.code','=','UY')]", copy=False)
