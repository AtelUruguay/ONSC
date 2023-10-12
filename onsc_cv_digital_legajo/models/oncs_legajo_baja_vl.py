# -*- coding:utf-8 -*-
import logging

from email_validator import EmailNotValidError, validate_email

from odoo import models, _

_logger = logging.getLogger(__name__)


class ONSCLegajoBajaVL(models.Model):
    _inherit = 'onsc.legajo.baja.vl'

    def get_followers_mails(self):
        CVDigital = self.env['onsc.cv.digital'].sudo()
        followers_emails = []
        for follower in self.message_follower_ids:
            try:
                cv_digital = CVDigital.search([('partner_id', '=', follower.partner_id.id), ('type', '=', 'cv')],
                                              limit=1)
                if cv_digital.institutional_email:
                    partner_email = cv_digital.institutional_email
                else:
                    partner_email = follower.partner_id.email
                validate_email(partner_email)
                followers_emails.append(partner_email)
            except EmailNotValidError:
                # Si el email no es válido, se captura la excepción
                _logger.info(_("Mail de Contacto no válido: %s") % follower.partner_id.email)
        return ','.join(followers_emails)
