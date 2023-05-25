# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS12(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws12'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS12'

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS12_consultaAuditoriaCGN')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")

        wsclient = self._get_client(parameter, '', integration_error)

        for alta_vl in self.env['onsc.legajo.alta.vl'].suspend_security().search([
            ('state', '=', 'pendiente_auditoria_cgn')], limit=100):
            self.with_context(alta_vl = alta_vl, log_info=log_info).suspend_security()._syncronize(wsclient, parameter, '',
                                                                                integration_error, alta_vl.id_alta)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            if not hasattr(response, 'movimiento'):
                return "No se obtuvieron vacantes con los datos enviados"
            alta_vl = self._context.get('alta_vl')
            if response.movimiento and alta_vl.id_alta == str(response.movimiento.pdaId):
                if response.movimiento.estado == 'AUDITADO':
                    alta_vl.action_aprobado_cgn()
                elif response.movimiento.estado == 'RECHAZADO':
                    alta_vl.action_rechazado_cgn()
