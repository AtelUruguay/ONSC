# -*- coding:utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ONSCLegajoBajaVL(models.Model):
    _inherit = 'onsc.legajo.baja.vl'

    def get_followers_mails(self):
        return self.message_follower_ids.mapped('partner_id').get_onsc_mails()
