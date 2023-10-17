# -*- coding: utf-8 -*-

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_email_recipient_values(self, recipient_ids):
        if self._name in ['onsc.legajo.alta.vl', 'onsc.legajo.baja.vl']:
            email_to = self.env['res.partner'].browse(recipient_ids).get_onsc_mails()
            return {
                'email_to': email_to,
                'recipient_ids': recipient_ids,
            }
        else:
            return super(MailThread, self)._notify_email_recipient_values(recipient_ids)
