# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoPadronEstructureFilterWizard(models.TransientModel):
    _name = 'onsc.legajo.padron.estructure.filter.wizard'
    _description = 'Wizard para filtrar estructuras de padron'

    inciso_id = fields.Many2one('onsc.legajo.inciso', string='Inciso')
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Unidad Ejecutora',
        domain="[('inciso_id', '=', inciso_id)]"
    )
    department_id = fields.Many2one(
        'onsc.legajo.department',
        string='Departamento',
        domain="[('operating_unit_id', '=', operating_unit_id)]"
    )

    @api.onchange('inciso_id')
    def _onchange_inciso_id(self):
        self.operating_unit_id = False

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        self.department_id = False

    def action_show(self):
        return True

