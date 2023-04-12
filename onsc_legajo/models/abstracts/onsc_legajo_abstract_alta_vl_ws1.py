# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSync(models.AbstractModel):
    _name = 'onsc.legajo.abstract.alta.vl.ws1'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS1'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS1_plazasVacantesCedula')
        # cron = self.env.ref("onsc_legajo.sync_legajo_regime")
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")

        wsclient = self._get_client(parameter, '', integration_error)
        # TODO: cuando intente hacer un update a data no me funciono, por eso lo hice asi

        if record.is_reserva_sgh:
            data = {
                'fechaAlta': record.date_start.strftime('%d/%m/%Y'),
                'nroPuesto': record.nroPuesto or '0',
                'nroPlaza': record.nroPlaza or '0',
                'cedula': record.cv_nro_doc or '',
                'inciso': record.inciso_id.budget_code or '0',
                'ue': record.operating_unit_id.budget_code or '0',
                'programa': record.programa or '0',
                'proyecto': record.proyecto or '0',
            }
        else:
            data = {
                'fechaAlta': record.date_start.strftime('%d/%m/%Y'),
                'codigoRegimen': record.regime_id.codRegimen if record.regime_id else '',
                'dsc1Id': '900',
                'dsc2Id': '1',
                'inciso': record.inciso_id.budget_code or '0',
                'ue': record.operating_unit_id.budget_code or '0',
                'programa': record.programa or '0',
                'proyecto': record.proyecto or '0',
            }

        return self.with_context(log_info=log_info).suspend_security()._syncronize(wsclient, parameter, '',
                                                                                   integration_error, data)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit

        integration_error_WS14_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9000")
        integration_error_WS14_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9001")
        integration_error_WS14_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9002")

        with self._cr.savepoint():
            if not hasattr(response, 'listaPlazas'):
                return False
            vacante_ids = [(5,)]
            for external_record in response.listaPlazas:
                try:
                    regimen_id = self.env['onsc.legajo.regime'].search(
                        [('codRegimen', '=', external_record.Regimen.codRegimen)], limit=1)

                    data = {
                        'nroPuesto': external_record.nroPuesto,
                        'nroPlaza': external_record.nroPlaza,
                        'codPartida': external_record.partida.codPartida if hasattr(external_record.partida,
                                                                                    'codPartida') else '',
                        # 'fechaReserva': external_record.fechaReserva,
                        'Dsc3Id': external_record.partida.dsc3Id if hasattr(external_record.partida, 'dsc3Id') else '',
                        'Dsc3Descripcion': external_record.partida.dsc3Descripcion if hasattr(external_record.partida,
                                                                                              'dsc3Descripcion') else '',
                        'Dsc4Id': external_record.partida.dsc4Id if hasattr(external_record.partida, 'dsc4Id') else '',
                        'Dsc4Descripcion': external_record.partida.dsc4Descripcion if hasattr(external_record.partida,
                                                                                              'dsc4Descripcion') else '',
                        'regime_id': regimen_id.id,
                        'descripcionJornadaFormal': external_record.descripcionJornadaFormal,
                    }

                    vacante_ids.append((0, 0, data))
                    if self._context.get('log_info'):
                        self.create_new_log(
                            origin='',
                            type='info',
                            integration_log=integration_error_WS14_9000,
                            ws_tuple=external_record,
                            long_description='Evento: Creación'
                        )
                except Exception as e:
                    _logger.warning(tools.ustr(e))
                    self.create_new_log(
                        origin='',
                        type='error',
                        integration_log=integration_error_WS14_9001,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
            return vacante_ids
