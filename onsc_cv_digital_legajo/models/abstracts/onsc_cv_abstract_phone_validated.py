# -*- coding: utf-8 -*-

from odoo import models


class ONSCCVLegajoAbstractPhoneValidated(models.AbstractModel):
    _inherit = 'onsc.cv.abstract.phone.validated'

    def onchange_validate_phone(self, prefix_phone_id, phone):
        if phone != 'emergency_service_telephone':
            return super(ONSCCVLegajoAbstractPhoneValidated,
                         self).onchange_validate_phone(prefix_phone_id, phone)
