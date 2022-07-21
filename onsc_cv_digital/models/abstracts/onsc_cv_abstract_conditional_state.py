# -*- coding: utf-8 -*-

from odoo import fields, models, api
from .. import onsc_cv_useful_tools as useful_tools
from .onsc_cv_abstract_config import STATES as CONDITIONAL_VALIDATION_STATES


class ONSCCVAbstractConditionalState(models.AbstractModel):
    _name = 'onsc.cv.abstract.conditional.state'
    _description = 'Modelo abstracto de estado condicional'
    _catalogs2validate = []

    # CATALOGS VALIDATION STATE
    conditional_validation_state = fields.Selection(
        string="Estado valor condicional",
        selection=CONDITIONAL_VALIDATION_STATES,
        compute='_compute_conditional_validation_state',
        store=True
    )
    conditional_validation_reject_reason = fields.Html(
        string="Motivo del rechazo",
        compute='_compute_conditional_validation_state',
        store=True
    )

    @api.depends(lambda self: ['%s.state' % x for x in self._catalogs2validate])
    def _compute_conditional_validation_state(self):
        for record in self:
            validation_status = useful_tools.get_validation_status(record, self._catalogs2validate)
            record.conditional_validation_state = validation_status.get('state')
            record.conditional_validation_reject_reason = validation_status.get('reject_reason', '')
