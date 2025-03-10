# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
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

    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_ue')

    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_inciso_ue_uo_consult')

    def action_show(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'onsc.legajo.department',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('inciso_id', '=', self.inciso_id.id), ('operating_unit_id', '=', self.operating_unit_id.id)],
            'context': {'is_from_menu': True, 'is_legajo': True, 'active_test': False, 'ignore_base_restrict': True},
            'views': [
                [self.env.ref('onsc_legajo.onsc_legajo_department_tree').id, 'tree'],
            ]
        }
