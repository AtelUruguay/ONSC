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
            'inciso': record.inciso_id.budget_code,
            'ue': record.operating_unit_id.budget_code,
            'descripcion': 'prueba WS',
            'presupuestales': 'S' if record.is_presupuestado else 'N',
            'altaDetalle': [
                {'fechaAlta': record.date_start.strftime('%d/%m/%Y'),
                 'cedula': record.partner_id.cv_nro_doc[:-1],
                 'digitoVerificador': record.partner_id.cv_nro_doc[-1],
                 'primerApellido': record.partner_id.cv_last_name_1,
                 }]
        }
        if record.partner_id.cv_last_name_2:
            data['altaDetalle'][0].update({
                'segundoApellido': record.partner_id.cv_last_name_2
            })
        data['altaDetalle'][0].update({
            'primerNombre': record.partner_id.cv_first_name,
        })
        if record.partner_id.cv_second_name:
            data['altaDetalle'][0].update({
                'segundoNombre': record.partner_id.cv_second_name
            })
        if record.regime_id and record.regime_id.codRegimen:
            data['altaDetalle'][0].update({
                'codRegimen': record.regime_id.codRegimen,
            })

        if record.partida_id and record.partida_id.codPartida:
            data['altaDetalle'][0].update({
                'codPartida': record.partida_id.codPartida,
            })

        if record.is_presupuestado:
            data['altaDetalle'][0].update({
                'nroPuesto': record.nroPuesto,
                'nroPlaza': record.nroPlaza,
            })

        data['altaDetalle'][0].update({
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
            data['altaDetalle'][0].update({
                'codigoEstadoCivil': record.marital_status_id.code,
            })

        data['altaDetalle'][0].update({
            'fechaDeNacimiento': record.cv_birthdate.strftime('%d/%m/%Y'),
            'sexo': 'M' if record.cv_sex == 'male' else 'F',
        })

        if record.country_of_birth_id.name:
            data['altaDetalle'][0].update({
                'lugarDeNacimiento': record.country_of_birth_id.name,
            })

        data['altaDetalle'][0].update({
            'tipoCiudadania': 'N',  # FIXME Hardcode WS4 solo permite nacionalidad uruguaya
            'nacionalidad': 'URUGUAYA',  # FIXME Hardcode WS4 solo permite nacionalidad uruguaya
            'serieCredencial': record.crendencial_serie,
            'numeroCredencial': record.credential_number,
        })

        if record.personal_phone:
            data['altaDetalle'][0].update({
                'telefonoAlternativo': record.personal_phone,
            })
        if record.mobile_phone:
            data['altaDetalle'][0].update({
                'telefonoMovil': record.mobile_phone,
            })

        if record.cv_address_street_id and record.cv_address_street_id.code:
            calleCod = record.cv_address_street_id.code
        elif record.cv_address_street:
            calleCod = record.cv_address_street
        else:
            calleCod = '9999999999'
        data['altaDetalle'][0].update({
            'eMail': record.email,
            'deptoCod': record.cv_address_state_id.code or '99',
            # TODO default 99 : record.cv_address_state_id.code or '99', Codigo de departamento  en nuestro catalogo son string
            'localidadCod': record.cv_address_location_id.code if record.cv_address_location_id and record.cv_address_location_id.code else '9999999999',
            'calleCod': calleCod,
        })

        if record.cv_address_nro_door:
            data['altaDetalle'][0].update({
                'numeroDePuerta': record.cv_address_nro_door,
            })
        if record.cv_address_street2_id and record.cv_address_street2_id.code:
            data['altaDetalle'][0].update({
                'callCodEntre1': record.cv_address_street2_id.code,
            })
        if record.cv_address_street3_id and record.cv_address_street3_id.code:
            data['altaDetalle'][0].update({
                'callCodEntre2': record.cv_address_street3_id.code,
            })

        data['altaDetalle'][0].update({
            'bis': '1' if record.cv_address_is_cv_bis else '0',
        })

        if record.cv_address_apto:
            data['altaDetalle'][0].update({
                'apto': record.cv_address_apto,
            })
        if record.cv_address_place:
            data['altaDetalle'][0].update({
                'paraje': record.cv_address_place,
            })
        if record.cv_address_zip:
            data['altaDetalle'][0].update({
                'codigoPostal': record.cv_address_zip,
            })

        if record.cv_address_block:
            data['altaDetalle'][0].update({
                'manzana': record.cv_address_block,
            })

        if record.cv_address_sandlot:
            data['altaDetalle'][0].update({
                'solar': record.cv_address_sandlot,
            })

        if record.health_provider_id and record.health_provider_id.code:
            data['altaDetalle'][0].update({
                'mutuCod': record.health_provider_id.code,
            })
        else:
            data['altaDetalle'][0].update({
                'mutuCod': '99',
            })

        if record.date_income_public_administration:
            data['altaDetalle'][0].update({
                'fechaDeIngresoAlaAdm': record.date_income_public_administration.strftime('%d/%m/%Y')
            })

        if record.inactivity_years:
            data['altaDetalle'][0].update({
                'aniosInactividad': record.inactivity_years,
            })

        if record.department_id and record.department_id.code:
            data['altaDetalle'][0].update({
                'UO': record.department_id.code,
            })

        if record.contract_expiration_date:
            data['altaDetalle'][0].update({
                'fechaVencimientoDelContrato': record.contract_expiration_date.strftime('%d/%m/%Y'),
            })
        if record.codigoJornadaFormal:
            data['altaDetalle'][0].update({
                'jornadaReal': record.codigoJornadaFormal,
            })
        data['altaDetalle'][0].update({
            'jornadaRetributiva': record.retributive_day_id.codigoJornada,
            'responsableUO': 'S' if record.is_responsable_uo else 'N',
            'codigoOcupacion': record.occupation_id.code,
        })
        if record.graduation_date:
            data['altaDetalle'][0].update({
                'fechaGradAsig': record.graduation_date.strftime('%d/%m/%Y')
            })

        _logger.info('******************WS4')
        _logger.info(data)
        _logger.info('******************WS4')
        return self.with_context(log_info=log_info).suspend_security()._syncronize(wsclient, parameter, 'WS4',
                                                                                   integration_error, data)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        with self._cr.savepoint():
            if not hasattr(response, 'altaSGHMovimientoRespuesta'):
                return "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."

            if response.altaSGHMovimientoRespuesta:
                for external_record in response.altaSGHMovimientoRespuesta:
                    try:
                        return external_record
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        return "Error devuelto por SGH: %s" % tools.ustr(e)

            else:
                return "No se obtuvo respuesta del servicio web"
            return False
