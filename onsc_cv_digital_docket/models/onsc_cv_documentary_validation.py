# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError

DOCUMENTARY_VALIDATION_STATES = [('to_validate', 'Para validar'),
                                 ('validated', 'Validado'),
                                 ('rejected', 'Rechazado')]


class ONSCCVAbstractFileValidation(models.AbstractModel):
    _inherit = 'onsc.cv.abstract.documentary.validation'

    def _check_todisable_dynamic_fields(self):
        return super(ONSCCVAbstractFileValidation, self)._check_todisable_dynamic_fields() or self.cv_digital_id.is_docket

