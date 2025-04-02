# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval

from odoo.exceptions import UserError, ValidationError
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

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

    @api.onchange('date')
    def _onchange_dates(self):
        if self.date and self.date > fields.Date.today():
            self.date = fields.Date.today()
            return cv_warning(_("La fecha no puede ser mayor a la fecha actual."))

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


class ONSCLegajoPadronEstructureMovementsFilterWizard(models.TransientModel):
    _name = 'onsc.legajo.padron.estructure.movements.filter.wizard'
    _inherit = 'onsc.legajo.abstract.opaddmodify.security'
    _description = 'Wizard para filtrar estructuras de padron'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Unidad Ejecutora'
    )
    date_from = fields.Date(string='Fecha de inicio', required=True)
    date_to = fields.Date(string='Fecha de fin', required=True)

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            self.date_to = False
            return cv_warning(_("La fecha hasta no puede ser menor a la fecha desde."))
        if self.date_from and self.date_from > fields.Date.today():
            self.date_from = False
            return cv_warning(_("La fecha desde no puede ser mayor a la fecha actual."))
        if self.date_to and self.date_to > fields.Date.today():
            self.date_to = False
            return cv_warning(_("La fecha hasta no puede ser mayor a la fecha actual."))

    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_movements_consult')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_movements_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_report_padron_movements_ue')

    def action_show(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_padron_movements_action').sudo().read()[0]
        # Obtener el contexto original de la acción (puede estar como cadena JSON)
        original_context = safe_eval(action.get('context', '{}'))

        # Fusionar el contexto original con el contexto actual y los nuevos valores
        new_context = {
            **original_context,
            **self.env.context,
            'operating_unit_id': self.operating_unit_id.id,
            'inciso_id': self.inciso_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        if not self.operating_unit_id:
            new_context['search_default_group_operating_unit_id'] = True
        action['context'] = new_context
        return action
