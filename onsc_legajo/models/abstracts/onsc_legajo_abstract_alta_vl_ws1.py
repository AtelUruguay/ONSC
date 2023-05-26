# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncW1(models.AbstractModel):
    _name = 'onsc.legajo.abstract.alta.vl.ws1'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS1'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS1_plazasVacantesCedula')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS1_9005")

        wsclient = self._get_client(parameter, '', integration_error)
        # TODO: cuando intente hacer un update a data no me funciono, por eso lo hice asi

        data = {
            'fechaAlta': record.date_start.strftime('%d/%m/%Y'),
        }

        if record.is_reserva_sgh:
            if record.nroPuesto:
                data.update({
                    'nroPuesto': record.nroPuesto,
                })
            if record.nroPlaza:
                data.update({
                    'nroPlaza': record.nroPlaza,
                })
            if record.partner_id:
                data.update({
                    'cedula': record.partner_id.cv_nro_doc[:-1],
                })
        else:
            if record.regime_id:
                data.update({
                    'codigoRegimen': record.regime_id.codRegimen,
                })
            if record.descriptor1_id:
                data.update({
                    'dsc1Id': record.descriptor1_id.code,
                })
            if record.descriptor2_id:
                data.update({
                    'dsc2Id': record.descriptor2_id.code,
                })

        data.update({
            'inciso': record.inciso_id.budget_code or '0',
            'ue': record.operating_unit_id.budget_code or '0',
            'programa': record.program_project_id.programa or '',
            'proyecto': record.program_project_id.proyecto or '',
        })

        return self.with_context(alta_vl=record, log_info=log_info).suspend_security()._syncronize(wsclient, parameter,
                                                                                                   'WS1',
                                                                                                   integration_error,
                                                                                                   data)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            onsc_legajo_integration_error_WS1_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS1_9004")
            if not hasattr(response, 'listaPlazas'):
                self.create_new_log(
                    origin='WS1',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS1_9004,
                    long_description="No se obtuvieron vacantes con los datos enviados."
                )
                return "No se obtuvieron vacantes con los datos enviados."
            vacante_ids = [(5,)]
            if response.listaPlazas:
                for external_record in response.listaPlazas:
                    # TODO la fecha de reserva y vacante no se esta sincronizando.Revisar como convertir el string a date
                    try:
                        data = {
                            'nroPuesto': external_record.nroPuesto,
                            'nroPlaza': external_record.nroPlaza,
                            'codPartida': external_record.partida.codPartida if hasattr(external_record.partida,
                                                                                        'codPartida') else '',
                            'Dsc3Id': external_record.partida.dsc3Id if hasattr(external_record.partida,
                                                                                'dsc3Id') else '',
                            'Dsc3Descripcion': external_record.partida.dsc3Descripcion if hasattr(
                                external_record.partida,
                                'dsc3Descripcion') else '',
                            'Dsc4Id': external_record.partida.dsc4Id if hasattr(external_record.partida,
                                                                                'dsc4Id') else '',
                            'Dsc4Descripcion': external_record.partida.dsc4Descripcion if hasattr(
                                external_record.partida,
                                'dsc4Descripcion') else '',
                            'codigoJornadaFormal': external_record.codigoJornadaFormal,
                            'descripcionJornadaFormal': external_record.descripcionJornadaFormal,
                            'descripcionRegimen': external_record.Regimen.descripcionRegimen,
                            'codRegimen': external_record.Regimen.codRegimen,
                            'estado': external_record.estado if hasattr(external_record, 'estado') else '',
                            'estadoDescripcion': external_record.estadoDescripcion if hasattr(external_record,
                                                                                              'estadoDescripcion') else '',
                            'fechaVacantePLaza': datetime.datetime.strptime(external_record.fechaVacantePLaza,
                                                                            '%d/%m/%Y').date() if hasattr(
                                external_record, 'fechaVacantePLaza') else False,
                            'fechaReserva': datetime.datetime.strptime(external_record.fechaReserva,
                                                                       '%d/%m/%Y').date() if hasattr(external_record,
                                                                                                     'fechaReserva') else False,
                        }
                        vacante_ids.append((0, 0, data))
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin='WS1',
                            type='error',
                            integration_log=onsc_legajo_integration_error_WS1_9004,
                            long_description="Error al sincronizar vacantes: %s" % tools.ustr(e)
                        )
                        return "Error al sincronizar vacantes"
            else:
                alta_vl = self._context.get('alta_vl')
                self.create_new_log(
                    origin='WS1',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS1_9004,
                    long_description="No se encontraron vacantes para el Alta de vínculo laboral con identificador: %s" % (
                        str(alta_vl.id))
                )
                return "No se encontraron vacantes"
            return vacante_ids
