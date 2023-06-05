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
        for baja_vl in self.env['onsc.legajo.baja.vl'].suspend_security().search([
            ('state', '=', 'pendiente_auditoria_cgn')], limit=100):

            self.with_context(baja_vl=baja_vl, log_info=log_info).suspend_security()._syncronize(
                wsclient, parameter,
                'WS12',
                integration_error,
                baja_vl.id_baja)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            integration_error_WS12_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS12_9000")
            alta_vl = self._context.get('alta_vl')
            onsc_legajo_integration_error_WS12_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS12_9004")
            if self._context.get('alta_vl'):
                accion = self._context.get('alta_vl')
                id_accion = accion.id_alta
            else:
                accion = self._context.get('baja_vl')
                id_accion = accion.id_baja

            if not hasattr(response, 'movimiento'):
                self.create_new_log(
                    origin='WS12',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS12_9004,
                    long_description="No se obtuvo info con los datos enviados para el pdaID: %s" % str(
                        id_accion))
                return True
            if response.movimiento and id_accion != str(response.movimiento.pdaId):
                self.create_new_log(
                    origin='WS12',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS12_9004,
                    long_description="El pdaID devuelto(%s) no coincide con el pdaID solicitado(%s)" % (
                        str(response.movimiento.pdaId), str(id_accion)))
                return True
            if response.movimiento.estado.upper() == 'AUDITADO':
                if accion.secPlaza != str(response.movimiento.secPlaza):
                    accion.secPlaza = str(response.movimiento.secPlaza)
                accion.action_aprobado_cgn()
            elif response.movimiento.estado.upper() == 'RECHAZADO':
                accion.action_rechazado_cgn()
            if self._context.get('log_info'):
                self.create_new_log(
                    origin='WS12',
                    type='info',
                    integration_log=integration_error_WS12_9000,
                    ws_tuple=id_accion,
                    long_description='Evento: %s' % response.movimiento.estado.upper()
                )
