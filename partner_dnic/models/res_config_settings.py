# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, _
from odoo.exceptions import ValidationError

from ..soap import dnic_client

_logger = logging.getLogger(__name__)

CI_TEST = '11745679'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_dnic_integrated = fields.Boolean(related="company_id.is_dnic_integrated", readonly=False)
    dnic_wsdl = fields.Char(related="company_id.dnic_wsdl", readonly=False)
    dnic_organization = fields.Char(related="company_id.dnic_organization", readonly=False)
    dnic_password = fields.Char(related="company_id.dnic_password", readonly=False)
    dnic_doc_type = fields.Selection(related="company_id.dnic_doc_type", readonly=False)

    def button_test_dnic(self):
        try:
            client_obj = dnic_client.DNICClient(self.env.company)
            response = client_obj.ObtPersonaPorDoc(CI_TEST)
            if response:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'title': _("Servicio DNIC"),
                        'message': _('Conexión exitosa'),
                        'next': {
                            'type': 'ir.actions.act_window_close'
                        },
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Servicio DNIC conexión fallida"),
                        'type': 'warning',
                        'sticky': True,  # True/False will display for few seconds if false
                        'next': {'type': 'ir.actions.act_window_close'},
                    },
                }

        except Exception as ex:
            _logger.debug("DNIC ERROR: %s" % ex)
            raise ValidationError(_("Ha ocurrido un error al conectarse a DNIC"))
