# -*- coding: utf-8 -*-

import logging

from odoo import models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWSRVE(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws.rve'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con RVE'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS_RVE_historialegajo')
        pe_user = self.env['ir.config_parameter'].sudo().get_param('parameter_ws_rve_user')
        pe_pass = self.env['ir.config_parameter'].sudo().get_param('parameter_ws_rve_pass')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS_RVE_9005")

        wsclient = self._get_client(parameter, '', integration_error, pass_location=True)

        if self._context.get('test'):
            # FIXME: Hardcoded
            data = {
                'Pe_user': pe_user,
                'Pe_pass': pe_pass,
                'Pe_pais': record.emissor_country_id.code_rve,
                'Pe_tpodoc': record.document_type_id.code_other,
                'Pe_docnum': '56043721',
            }
        else:
            data = {
                'Pe_user': pe_user,
                'Pe_pass': pe_pass,
                'Pe_pais': record.emissor_country_id.code_rve,
                'Pe_tpodoc': record.document_type_id.code_other,
                'Pe_docnum': record.nro_doc,
            }
        self = self.with_context(
            legajo=record,
            log_info=log_info,
            simpleWsdl=True,
            use_execute_with_args=True).suspend_security()
        return self._syncronize(
            wsclient,
            parameter,
            'WS_RVE',
            integration_error,
            data,
            always_return_result=True
        )

    def _populate_from_syncronization(self, response):
        if not hasattr(response, 'Ps_datoshcopdf'):
            raise ValidationError(_("Error al obtener el PDF"))
        if hasattr(response, 'Ps_errnum') and response['Ps_errnum'] != 0:
            raise ValidationError(response['Ps_errdsc'])
        return response['Ps_datoshcopdf']
