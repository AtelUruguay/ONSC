# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncW4(models.AbstractModel):
    _name = 'onsc.legajo.abstract.alta.vl.ws4'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS5'

    @api.model
    def syncronize(self, record, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS4_altaSGH')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")

        wsclient = self._get_client(parameter, '', integration_error)

        data = {
            'inciso': record.inciso_id.budget_code or '0',
            'ue': record.operating_unit_id.budget_code or '0',
            'descripcion': 'prueba WS',
            'presupuestales': 'S' if record.is_presupuestado else 'N',
            'altaDetalle': [
                {'fechaAlta': record.date_start.strftime('%d/%m/%Y') if record.date_start else '',
                 'cedula': record.partner_id.cv_nro_doc[:-1] or '',
                 'digitoVerificador': record.partner_id.cv_nro_doc[-1] or '',
                 'primerApellido': record.partner_id.cv_last_name_1 or '',
                 'segundoApellido': record.partner_id.cv_last_name_2 or '',
                 'primerNombre': record.partner_id.cv_first_name or '',
                 'segundoNombre': record.partner_id.cv_second_name or '',
                 'codRegimen': record.regime_id.codRegimen or '',
                 'codPartida': record.partida_id.codPartida or '',
                 }]
        }
        if record.is_presupuestado:
            data['altaDetalle'][0].update({
                'nroPuesto': record.nroPuesto or '0',
                'nroPlaza': record.nroPlaza or '0',
            })

        data['altaDetalle'][0].update({
            'programa': record.program_id.programa or '0',
            'proyecto': record.project_id.proyecto or '0',
            'descripcionMotivo': record.reason_description,
            'numeroNorma': record.norm_number or '',
            'articuloNorma': record.norm_article or '',
            'tipoNormaSigla': record.norm_id.tipoNormaSigla or '',
            'anioNorma': str(record.norm_year) or '',
            'descripcionResolucion': record.resolution_description or '',
            'fechaResolucion': record.resolution_date.strftime('%d/%m/%Y') if record.resolution_date else '',
            'tipoResolucion': record.resolution_type or '',
            'codigoEstadoCivil': record.marital_status_id.code or '1',
            'fechaDeNacimiento': record.cv_birthdate.strftime('%d/%m/%Y') if record.cv_birthdate else '',
            'sexo': record.cv_sex or 'M',
            'lugarDeNacimiento': record.country_of_birth_id.name or 'URUGUAY',
            'tipoCiudadania': 'N',
            'nacionalidad': 'URUGUAYA',
            'serieCredencial': record.crendencial_serie or '',
            'numeroCredencial': record.credential_number or '',
            'telefonoAlternativo': record.personal_phone or '',
            'telefonoMovil': record.mobile_phone or '',
            'eMail': record.email or '',
            'deptoCod': '10',
            # TODO record.cv_address_state_id.code or '0', Codigo de departamento  en nuestro catalogo son string
            'localidadCod': record.cv_address_location_id.code or '0',
            'calleCod': record.cv_address_street_id.code or '0',
            'numeroDePuerta': record.cv_address_nro_door or '0',
            'callCodEntre1': record.cv_address_street2_id.code or '0',
            'callCodEntre2': record.cv_address_street3_id.code or '0',
            'bis': '1' if record.cv_address_is_cv_bis else '0',
            'apto': record.cv_address_apto or '0',
            'paraje': record.cv_address_place or '0',
            'codigoPostal': record.cv_address_zip or '0',
            'manzana': record.cv_address_block or '0',
            'solar': record.cv_address_sandlot or '0',
            'mutuCod': '3',  # TODO no encontre mutualista en el catalogo
            'fechaDeIngresoAlaAdm': record.date_income_public_administration.strftime(
                '%d/%m/%Y') if record.date_income_public_administration else '',
            'aniosInactividad': record.inactivity_years or '0',
            'UO': record.department_id.code or '0',
        })

        if record.contract_expiration_date:
            data['altaDetalle'][0].update({
                'fechaVencimientoDelContrato': record.contract_expiration_date.strftime(
                    '%d/%m/%Y') if record.contract_expiration_date else '',
            })

        data['altaDetalle'][0].update({
            'jornadaReal': '240',  # TODO buscar de donde sale
            'jornadaRetributiva': record.retributive_day_id.codigoJornada or '0',
            'responsableUO': 'S' if record.is_responsable_uo else 'N',
            'codigoOcupacion': record.occupation_id.code or '0',
            'fechaGradAsig': '01/01/2025',  # TODO buscar de donde sale
        })

        return self.with_context(log_info=log_info).suspend_security()._syncronize(wsclient, parameter, '',
                                                                                   integration_error, data)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit

        integration_error_WS14_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9000")
        integration_error_WS14_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9001")
        integration_error_WS14_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9002")

        with self._cr.savepoint():
            if not hasattr(response, 'altaSGHMovimientoRespuesta'):
                return "No se pudo conectar con el servicio web"

            if response.altaSGHMovimientoRespuesta:
                for external_record in response.altaSGHMovimientoRespuesta:
                    try:
                        print(external_record)
                        if self._context.get('log_info'):
                            self.create_new_log(
                                origin='',
                                type='info',
                                integration_log=integration_error_WS14_9000,
                                ws_tuple=external_record,
                                long_description='Evento: Creación'
                            )
                        return external_record
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin='',
                            type='error',
                            integration_log=integration_error_WS14_9001,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
                        return "Error al sincronizar con el servicio web"

            else:
                return "No se obtuvo respuesta del servicio web"
            return False
