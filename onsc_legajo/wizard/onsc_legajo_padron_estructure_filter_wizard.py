# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval

from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoPadronEstructureFilterWizard(models.TransientModel):
    _name = 'onsc.legajo.padron.estructure.filter.wizard'
    _inherit = 'onsc.legajo.abstract.opaddmodify.security'
    _description = 'Wizard para filtrar estructuras de padron'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Unidad Ejecutora'
    )
    date = fields.Date(string='Fecha', required=True, default=lambda self: fields.Date.today())

    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')

    def action_show(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_padron_action').sudo().read()[0]
        # Obtener el contexto original de la acción (puede estar como cadena JSON)
        original_context = safe_eval(action.get('context', '{}'))

        # Fusionar el contexto original con el contexto actual y los nuevos valores
        new_context = {
            **original_context,
            **self.env.context,
            'operating_unit_id': self.operating_unit_id.id,
            'inciso_id': self.inciso_id.id,
            'date': self.date,
        }
        action['context'] = new_context
        return action
