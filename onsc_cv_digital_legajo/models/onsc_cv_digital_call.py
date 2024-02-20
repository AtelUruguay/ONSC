# -*- coding: utf-8 -*-

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ONSCCVDigitalCall(models.Model):
    _inherit = 'onsc.cv.digital.call'

    def _update_cv_digital_origin_documentary_values(self, documentary_field, vals):
        for record in self:
            cv_digital_origin_id = record.cv_digital_origin_id
            if cv_digital_origin_id and eval(
                    'cv_digital_origin_id.%s_write_date' % documentary_field) < record.create_date:
                cv_digital_origin_id.write(vals)
                documentary_state = getattr(cv_digital_origin_id,
                                            '%s_documentary_validation_state' % documentary_field,
                                            None)
                if documentary_state == 'validated':
                    cv_digital_origin_id.with_context(no_update_cv_calls=True).button_documentary_approve()
