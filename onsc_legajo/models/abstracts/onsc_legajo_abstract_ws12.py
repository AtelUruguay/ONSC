# -*- coding: utf-8 -*-

import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS12(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws12'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS12'

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS12_consultaAuditoriaCGN')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS12_9005")

        wsclient = self._get_client(parameter, 'WS12', integration_error)

        for alta_vl in self.env['onsc.legajo.alta.vl'].suspend_security().search([
            ('state', '=', 'pendiente_auditoria_cgn')], limit=100):
            self.with_context(alta_vl=alta_vl, log_info=log_info).suspend_security()._syncronize(
                wsclient, parameter,
                'WS12',
                integration_error,
                alta_vl.id_alta)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            integration_error_WS12_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS12_9000")
            alta_vl = self._context.get('alta_vl')
            onsc_legajo_integration_error_WS12_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS12_9004")
            if not hasattr(response, 'movimiento'):
                self.create_new_log(
                    origin='WS12',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS12_9004,
                    long_description="No se obtuvo info con los datos enviados para el pdaID: %s" % str(
                        alta_vl.id_alta))
                return True
            if response.movimiento and alta_vl.id_alta != str(response.movimiento.pdaId):
                self.create_new_log(
                    origin='WS12',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS12_9004,
                    long_description="El pdaID devuelto(%s) no coincide con el pdaID solicitado(%s)" % (
                        str(response.movimiento.pdaId), str(alta_vl.id_alta)))
                return True
            if response.movimiento.estado.upper() == 'AUDITADO':
                if alta_vl.secPlaza != str(response.movimiento.secPlaza):
                    alta_vl.secPlaza = str(response.movimiento.secPlaza)
                alta_vl.action_aprobado_cgn()
            elif response.movimiento.estado.upper() == 'RECHAZADO':
                alta_vl.action_rechazado_cgn()
            if self._context.get('log_info'):
                self.create_new_log(
                    origin='WS12',
                    type='info',
                    integration_log=integration_error_WS12_9000,
                    ws_tuple=alta_vl.id_alta,
                    long_description='Evento: %s' % response.movimiento.estado.upper()
                )
