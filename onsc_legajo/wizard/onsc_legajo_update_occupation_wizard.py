# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLegajoUpdateOccupationWizard(models.TransientModel):
    _name = 'onsc.legajo.update.occupation.wizard'
    _description = 'Actualización de ocupación de contrato'

    date = fields.Date(string="Fecha de actualización", required=True, default=lambda s: fields.Date.today())
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')

    def action_update_occupation(self):
        self._context.get('is_documentary_reject')

