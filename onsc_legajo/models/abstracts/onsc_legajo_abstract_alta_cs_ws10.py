# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncW10(models.AbstractModel):
    _name = 'onsc.legajo.abstract.alta.cs.ws10'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de alta cs con WS10'

    @api.model
    def syncronize(self, records, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS10_altaCS')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS10_9005")

        wsclient = self._get_client(parameter, 'WS10', integration_error)
        data = self._get_data(records)

        _logger.info('******************WS10')
        _logger.info(data)
        _logger.info('******************WS10')
        return self.with_context(altas_cs=records, log_info=log_info).suspend_security()._syncronize(
            wsclient,
            parameter,
            'WS10',
            integration_error,
            data)

    def _get_data(self, record):
        user_partner = self.env.user.partner_id
        cv_nro_doc_without_digit = user_partner.cv_nro_doc and user_partner.cv_nro_doc[:-1] or ''

        altaDetalle = {
            'cedula': record.partner_id.cv_nro_doc[:-1],
            'digitoVerificador': record.partner_id.cv_nro_doc[-1],
            'usuarioCedulaOdoo': cv_nro_doc_without_digit
        }
        if record.inciso_origin_id.is_central_administration:
            altaDetalle.update({
                'sec_plaza': record.contract_id.sec_position
            })
        altaDetalle.update({
            'primerApellido': record.partner_id.cv_last_name_1[:20],
        })
        if record.partner_id.cv_last_name_2:
            altaDetalle.update({
                'segundoApellido': record.partner_id.cv_last_name_2[:20]
            })
        altaDetalle.update({
            'primerNombre': record.partner_id.cv_first_name[:20],

        })
        if record.partner_id.cv_second_name:
            altaDetalle.update({
                'segundoNombre': record.partner_id.cv_second_name[:20]
            })

        altaDetalle.update({
            'sexo': 'M' if record.cv_sex == 'male' else 'F',
            'fechaNacimiento': record.cv_birthdate.strftime('%d/%m/%Y'),
        })

        if not record.inciso_origin_id.is_central_administration:
            altaDetalle.update({
                'codigoInstitucionOrigen': record.inciso_origin_id.budget_code,
            })

        altaDetalle.update({
            'fechaVigencia': record.date_start_commission.strftime('%d/%m/%Y'),
            'descripcionMotivo': record.reason_description or '',
            'numeroNorma': record.norm_number,
            'articuloNorma': record.norm_article,
            'tipoNormaSigla': record.norm_id.tipoNormaSigla,
            'anioNorma': str(record.norm_year),
            'descripcionResolucion': record.resolution_description,
            'fechaResolucion': record.resolution_date.strftime('%d/%m/%Y'),
            'tipoResolucion': record.resolution_type.upper(),
            'CodigoRegimenInicioComision': record.regime_commission_id.cgn_code,
            'origenEstaEnADM': 'S' if record.inciso_origin_id.is_central_administration else 'N',
            'destinoEstaEnADM': 'S' if record.inciso_destination_id.is_central_administration else 'N',
            'incisoDestino': record.inciso_destination_id.budget_code,
            'unidadEjecutoraDestino': record.operating_unit_destination_id.budget_code,
        })
        if record.program_project_destination_id:
            altaDetalle.update({
                'programaDestino': record.program_project_destination_id.programa,
                'proyectoDestino': record.program_project_destination_id.proyecto,
            })
        if not record.inciso_destination_id.is_central_administration:
            altaDetalle.update({
                'codigoInstitucionDestino': record.inciso_destination_id.budget_code,
            })
        altaDetalle.update({
            'tipoComision': record.type_commission_selection,
        })

        return altaDetalle

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            altas_cs = self._context.get('altas_cs')
            onsc_legajo_integration_error_WS10_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS10_9004")

            try:
                altas_cs.write({
                    'secPlaza': response['secPlazaDestino'] if 'secPlazaDestino' in response else False,
                    'nroPuesto': response['idPuestoDestino'] if 'idPuestoDestino' in response else False,
                    'nroPlaza': response['nroPlazaDestino'] if 'nroPlazaDestino' in response else False,
                })
                altas_cs.action_aprobado_cgn()
            except Exception as e:
                long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(
                    origin='WS10',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS10_9004,
                    long_description=long_description
                )
                self._process_error_alta_cs(long_description)

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        self._process_error_alta_cs(long_description)
        return super()._process_response_witherror(response, origin_name, integration_error,
                                                   long_description=long_description)

    def _process_servicecall_error(self, exception, origin_name, integration_error, long_description=''):
        self._process_error_alta_cs(long_description + tools.ustr(exception))
        super()._process_servicecall_error(exception, origin_name, integration_error, long_description=long_description)

    def _process_error_alta_cs(self, long_description):
        altas_cs = self._context.get('altas_cs')
        _error = long_description or "No se pudo conectar con el servicio web"
        altas_cs.write({
            'is_error_synchronization': True,
            'state': 'error_sgh',
            'error_message_synchronization': "Error devuelto por SGH: %s" % _error,
            'is_communicaton_error': long_description and False or True
        })
