# -*- coding: utf-8 -*-

import logging

from odoo import models, tools, api

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncW4(models.AbstractModel):
    _name = 'onsc.legajo.abstract.alta.vl.ws4'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS4'

    @api.model
    def syncronize_multi(self, records, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS4_altaSGH')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS4_9005")

        wsclient = self._get_client(parameter, 'WS4', integration_error)
        data = self._get_data_multi(records)

        _logger.info('******************WS4')
        _logger.info(data)
        _logger.info('******************WS4')
        return self.with_context(altas_vl=records, log_info=log_info).suspend_security()._syncronize(wsclient,
                                                                                                     parameter,
                                                                                                     'WS4',
                                                                                                     integration_error,
                                                                                                     data)

    def _get_data_multi(self, records):
        data = {
            'inciso': records[0].inciso_id.budget_code,
            'ue': records[0].operating_unit_id.budget_code,
            'descripcion': 'Alta masiva VL WS',
            'presupuestales': 'S' if records[0].is_presupuestado else 'N',

        }

        altasDetalle = []
        for record in records:
            altaDetalle = {'fechaAlta': record.date_start.strftime('%d/%m/%Y'),
                           'cedula': record.partner_id.cv_nro_doc[:-1],
                           'digitoVerificador': record.partner_id.cv_nro_doc[-1],
                           'primerApellido': record.partner_id.cv_last_name_1[:20],
                           }
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
            if record.regime_id and record.regime_id.codRegimen:
                altaDetalle.update({
                    'codRegimen': record.regime_id.codRegimen,
                })

            if record.partida_id and record.partida_id.codPartida:
                altaDetalle.update({
                    'codPartida': record.partida_id.codPartida,
                })

            if record.is_presupuestado:
                altaDetalle.update({
                    'nroPuesto': record.nroPuesto,
                    'nroPlaza': record.nroPlaza,
                })

            altaDetalle.update({
                'programa': record.program_project_id.programa,
                'proyecto': record.program_project_id.proyecto,
                'descripcionMotivo': record.reason_description,
                'numeroNorma': record.norm_number,
                'articuloNorma': record.norm_article,
                'tipoNormaSigla': record.norm_id.tipoNormaSigla,
                'anioNorma': str(record.norm_year),
                'descripcionResolucion': record.resolution_description,
                'fechaResolucion': record.resolution_date.strftime('%d/%m/%Y'),
                'tipoResolucion': record.resolution_type,

            })

            if record.marital_status_id and record.marital_status_id.code:
                altaDetalle.update({
                    'codigoEstadoCivil': record.marital_status_id.code,
                })

            altaDetalle.update({
                'fechaDeNacimiento': record.cv_birthdate.strftime('%d/%m/%Y'),
                'sexo': 'M' if record.cv_sex == 'male' else 'F',
            })

            if record.country_of_birth_id.name:
                altaDetalle.update({
                    'lugarDeNacimiento': record.country_of_birth_id.name,
                })

            altaDetalle.update({
                'tipoCiudadania': 'N',  # FIXME Hardcode WS4 solo permite nacionalidad uruguaya
                'nacionalidad': 'URUGUAYA',  # FIXME Hardcode WS4 solo permite nacionalidad uruguaya
                'serieCredencial': record.crendencial_serie,
                'numeroCredencial': record.credential_number,
            })

            if record.personal_phone:
                altaDetalle.update({
                    'telefonoAlternativo': record.personal_phone,
                })
            if record.mobile_phone:
                altaDetalle.update({
                    'telefonoMovil': record.mobile_phone,
                })

            if record.cv_address_street_id and record.cv_address_street_id.code:
                calleCod = record.cv_address_street_id.code
            elif record.cv_address_street:
                calleCod = record.cv_address_street
            else:
                calleCod = '9999999999'
            altaDetalle.update({
                'eMail': record.email,
                'deptoCod': record.cv_address_state_id.code or '99',
                # TODO default 99 : record.cv_address_state_id.code or '99', Codigo de departamento  en nuestro catalogo son string
                'localidadCod': record.cv_address_location_id.other_code if record.cv_address_location_id and record.cv_address_location_id.other_code else '9999999999',
                'calleCod': calleCod,
            })

            if record.cv_address_nro_door:
                altaDetalle.update({
                    'numeroDePuerta': record.cv_address_nro_door,
                })
            if record.cv_address_street2_id and record.cv_address_street2_id.code:
                altaDetalle.update({
                    'callCodEntre1': record.cv_address_street2_id.code,
                })
            if record.cv_address_street3_id and record.cv_address_street3_id.code:
                altaDetalle.update({
                    'callCodEntre2': record.cv_address_street3_id.code,
                })

            altaDetalle.update({
                'bis': '1' if record.cv_address_is_cv_bis else '0',
            })

            if record.cv_address_apto:
                altaDetalle.update({
                    'apto': record.cv_address_apto,
                })
            if record.cv_address_place:
                altaDetalle.update({
                    'paraje': record.cv_address_place,
                })
            if record.cv_address_zip:
                altaDetalle.update({
                    'codigoPostal': record.cv_address_zip,
                })

            if record.cv_address_block:
                altaDetalle.update({
                    'manzana': record.cv_address_block,
                })

            if record.cv_address_sandlot:
                altaDetalle.update({
                    'solar': record.cv_address_sandlot,
                })

            if record.health_provider_id and record.health_provider_id.code:
                altaDetalle.update({
                    'mutuCod': record.health_provider_id.code,
                })
            else:
                altaDetalle.update({
                    'mutuCod': '99',
                })

            if record.date_income_public_administration:
                altaDetalle.update({
                    'fechaDeIngresoAlaAdm': record.date_income_public_administration.strftime('%d/%m/%Y')
                })

            if record.inactivity_years:
                altaDetalle.update({
                    'aniosInactividad': record.inactivity_years,
                })

            if record.department_id and record.department_id.code:
                altaDetalle.update({
                    'UO': record.department_id.code,
                })

            if record.contract_expiration_date:
                altaDetalle.update({
                    'fechaVencimientoDelContrato': record.contract_expiration_date.strftime('%d/%m/%Y'),
                })
            if record.codigoJornadaFormal:
                altaDetalle.update({
                    'jornadaReal': record.codigoJornadaFormal,
                })
            altaDetalle.update({
                'jornadaRetributiva': record.retributive_day_id.codigoJornada,
                'responsableUO': 'S' if record.is_responsable_uo else 'N',
                'codigoOcupacion': record.occupation_id.code,
            })
            if record.graduation_date:
                altaDetalle.update({
                    'fechaGradAsig': record.graduation_date.strftime('%d/%m/%Y')
                })
            altasDetalle.append(altaDetalle)

        data['altaDetalle'] = altasDetalle
        return data

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            altas_vl = self._context.get('altas_vl')
            onsc_legajo_integration_error_WS4_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS4_9004")
            if hasattr(response, 'altaSGHMovimientoRespuesta') and response.altaSGHMovimientoRespuesta:
                for response in response.altaSGHMovimientoRespuesta:
                    try:
                        altas_vl_id = altas_vl.filtered(
                            lambda x: x.partner_id.cv_nro_doc[:-1] == str(response['cedula']))
                        if altas_vl_id:
                            altas_vl_id.write({
                                'id_alta': response['pdaId'] if 'pdaId' in response else False,
                                'secPlaza': response['secPlaza'] if 'secPlaza' in response else False,
                                'nroPuesto': response['idPuesto'] if 'idPuesto' in response else False,
                                'nroPlaza': response['nroPlaza'] if 'nroPlaza' in response else False,
                                'codigoJornadaFormal': response[
                                    'codigoJornadaFormal'] if 'codigoJornadaFormal' in response else False,
                                'descripcionJornadaFormal': response[
                                    'descripcionJornadaFormal'] if 'descripcionJornadaFormal' in response else False,
                                'is_error_synchronization': False,
                                'ws4_user_id': self.env.user.id,
                                'state': 'pendiente_auditoria_cgn',
                                'error_message_synchronization': ''
                            })
                    except Exception as e:
                        long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                        _logger.warning(long_description)
                        self.create_new_log(
                            origin='WS4',
                            type='error',
                            integration_log=onsc_legajo_integration_error_WS4_9004,
                            long_description=long_description
                        )
                        altas_vl.write({
                            'is_error_synchronization': True,
                            'state': 'error_sgh',
                            'error_message_synchronization': long_description
                        })

            else:
                long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
                self.create_new_log(
                    origin='WS4',
                    type='error',
                    integration_log=onsc_legajo_integration_error_WS4_9004,
                    long_description=long_description
                )
                altas_vl.write({
                    'is_error_synchronization': True,
                    'state': 'error_sgh',
                    'error_message_synchronization': long_description
                })

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        IntegrationError = self.env['onsc.legajo.integration.error']
        altas_vl = self._context.get('altas_vl')
        if hasattr(response, 'altaSGHMovimientoRespuesta'):
            for v_error in response.altaSGHMovimientoRespuesta:
                error = IntegrationError.search([
                    ('integration_code', '=', origin_name),
                    ('code_error', '=', str(v_error.codigo)),
                ], limit=1)
                message = error.description if error else v_error.mensaje
                self.create_new_log(
                    origin=origin_name,
                    type='error',
                    integration_log=error or integration_error,
                    ws_tuple=False,
                    long_description=v_error.mensaje)
                altas_vl_id = altas_vl.filtered(
                    lambda x: x.partner_id.cv_nro_doc[:-1] == str(v_error['cedula']))
                if altas_vl_id:
                    altas_vl_id.write({
                        'is_error_synchronization': True,
                        'state': 'error_sgh',
                        'error_message_synchronization': str(long_description) + "." + message
                    })
                else:
                    altas_vl.write({
                        'is_error_synchronization': True,
                        'state': 'error_sgh',
                        'error_message_synchronization': str(long_description) + "." + message
                    })
        else:
            altas_vl.write({
                'is_error_synchronization': True,
                'state': 'error_sgh',
                'error_message_synchronization': long_description
            })
            super(ONSCLegajoAbstractSyncW4, self)._process_response_witherror(
                response,
                origin_name,
                integration_error,
                long_description
            )
