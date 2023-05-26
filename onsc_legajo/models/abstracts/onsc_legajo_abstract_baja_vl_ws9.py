# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS9(models.AbstractModel):
    _name = 'onsc.legajo.abstract.baja.vl.ws9'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS9'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS9_bajaSGH')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS9_9005")

        wsclient = self._get_client(parameter, '', integration_error)

        for vl in record.employment_relationship_ids.filtered(lambda x: x.selected):

            data = {
                'fechaDeBaja': record.end_date.strftime('%d/%m/%Y'),
                'descripcionMotivo':record.reason_discharge,
                'numeroNorma': record.norm_number_discharge,
                'articuloNorma': record.norm_article_discharge,
                'tipoNormaSigla': record.type_norm_code_discharge,
                'anioNorma': record.norm_year_discharge,
                'descripcionResolucion': record.resolution_description_discharge,
                'fechaResolucion': record.resolution_date_discharge.strftime('%d/%m/%Y'),
                'tipoResolucion': record.resolution_type_discharge,
                'cedula': record.partner_id.cv_nro_doc,
                'secPlaza': vl.secPosition,
                'estadoLaboralBaja': record.causes_discharge_id.code_cgn
            }


            _logger.info('******************WS9')
            _logger.info(data)
            _logger.info('******************WS9')
            return self.with_context(log_info=log_info).suspend_security()._syncronize(wsclient, parameter, 'WS9',
                                                                                       integration_error, data)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            onsc_legajo_integration_error_WS9_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS9_9004")
            if not hasattr(response, 'servicioResultado'):
                self.create_new_log(
                    origin='WS4',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS9_9004,
                    long_description="No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
                )
                return "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."

            if response.pdaId:

                try:
                    return response.pdaId
                except Exception as e:
                    _logger.warning(tools.ustr(e))
                    self.create_new_log(
                        origin='WS4',
                        type='error',
                        integration_log=onsc_legajo_integration_error_WS9_9004,
                        long_description="Error devuelto por SGH: %s" % tools.ustr(e)
                    )
                    return "Error devuelto por SGH: %s" % tools.ustr(e)

            else:
                self.create_new_log(
                    origin='WS4',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS9_9004,
                    long_description="No se obtuvo respuesta del servicio web"
                )
                return "No se obtuvo respuesta del servicio web"
            return False
