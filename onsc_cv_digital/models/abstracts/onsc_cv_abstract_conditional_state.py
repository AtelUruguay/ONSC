# -*- coding: utf-8 -*-

from odoo import fields, models
from .. import onsc_cv_useful_tools as useful_tools
from .onsc_cv_abstract_config import STATES as CONDITIONAL_VALIDATION_STATES


class ONSCCVAbstractConditionalState(models.AbstractModel):
    _name = 'onsc.cv.abstract.conditional.state'
    _description = 'Modelo abstracto de estado condicional'

    # CATALOGS VALIDATION STATE
    conditional_validation_state = fields.Selection(
        string="Estado valor condicional",
        selection=CONDITIONAL_VALIDATION_STATES,
        compute='_compute_conditional_validation_state',
        store=True
    )
    conditional_validation_reject_reason = fields.Html(
        compute='_compute_conditional_validation_state',
        store=True
    )

    def _compute_conditional_validation_state(self, catalogs2validate_list=None):
        if catalogs2validate_list is None:
            catalogs2validate_list = []
        for record in self:
            validation_status = useful_tools._get_validation_status(record, catalogs2validate_list)
            record.conditional_validation_state = validation_status.get('state')
            record.conditional_validation_reject_reason = validation_status.get('reject_reason', '')
