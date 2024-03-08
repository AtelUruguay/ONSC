# -*- coding: utf-8 -*-

import logging

from odoo import models, api, tools

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS6_1(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws6.1'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS6.1'

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS6_1_modificacionDatosPersonales')
        WS6_1_9004 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS6_1_9004")
        WS6_1_9005 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS6_1_9005")

        wsclient = self._get_client(parameter, 'WS6.1', WS6_1_9005)
        Employee = self.env['hr.employee'].suspend_security()
        with self._cr.savepoint():
            Employee.search([('notify_sgh', '=', True), ('legajo_state', '!=', 'active')]).write({'notify_sgh': False})
            for record in Employee.search([('notify_sgh', '=', True), ('legajo_state', '=', 'active')]):
                try:
                    if record.cv_address_street_id:
                        calleCod = int(record.cv_address_street_id.code)
                    elif record.cv_address_street:
                        calleCod = int(record.cv_address_street)
                    else:
                        calleCod = 9999999999

                    if record.cv_address_location_id:
                        localidadCod = int(record.cv_address_location_id.other_code)
                    else:
                        localidadCod = 9999999999

                    if record.credential_number and record.credential_number.isdigit():
                        numeroCredencial = int(record.credential_number)
                    else:
                        numeroCredencial = 99999

                    data = {
                        'cedula': int(record.cv_nro_doc[:-1]),
                        'digitoVerificador': int(record.cv_nro_doc[-1]),
                        'primerApellido': record.cv_last_name_1[:20],
                        'primerNombre': record.cv_first_name[:20],
                        'sexo': 'M' if record.cv_sex == 'male' else 'F',
                        'tipoCiudadania': 'N',
                        'serieCredencial': record.crendencial_serie or 'ZZZ',
                        'numeroCredencial': numeroCredencial,
                        'localidadCod': localidadCod,
                        'calleCod': calleCod,
                        'mutuCod': record.health_provider_id and int(record.health_provider_id.code) or 99,
                        'bis': 1 if record.cv_address_is_cv_bis else 0
                    }
                    if record.cv_last_name_2:
                        data.update({'segundoApellido': record.cv_last_name_2[:20]})
                    if record.cv_second_name:
                        data.update({'segundoNombre': record.cv_second_name[:20]})
                    if record.cv_birthdate:
                        data.update({'fechaDeNacimiento': record.cv_birthdate.strftime('%d/%m/%Y')})
                    if record.country_of_birth_id:
                        data.update({'lugarDeNacimiento': record.country_of_birth_id.name})
                    if record.personal_phone:
                        data.update({'telefonoAlternativo': record.personal_phone})
                    if record.mobile_phone:
                        data.update({'telefonoMovil': record.mobile_phone})
                    if record.email:
                        data.update({'eMail': record.email})
                    data = self._get_data_address(record, data)
                    _logger.info('******************WS6.1')
                    _logger.info(data)
                    _logger.info('******************WS6.1')
                    self.with_context(employee=record, log_info=log_info).suspend_security()._syncronize(
                        wsclient,
                        parameter, 'WS6.1',
                        WS6_1_9004,
                        data)
                except Exception as e:
                    long_description = "Funcionario %s, Error al sincronizar WS6.1: %s" % (
                        record.display_name,
                        tools.ustr(e)
                    )
                    _logger.warning(long_description)
                    self.create_new_log(origin='WS6.1', type='error',
                                        integration_log=WS6_1_9004,
                                        long_description=long_description)

    def _get_data_address(self, record, data):
        if record.cv_address_street2_id:
            data.update({'callCodEntre1': int(record.cv_address_street2_id.code)})
        else:
            data.update({'callCodEntre1': 9999999999})
        if record.cv_address_street3_id:
            data.update({'callCodEntre2': int(record.cv_address_street3_id.code)})
        else:
            data.update({'callCodEntre2': 9999999999})
        if record.cv_address_apto:
            data.update({'apto': record.cv_address_apto})
        if record.cv_address_place:
            data.update({'paraje': record.cv_address_place})
        if record.cv_address_zip:
            data.update({'codigoPostal': int(record.cv_address_zip)})
        if record.cv_address_block:
            data.update({'manzana': int(record.cv_address_block)})
        if record.cv_address_sandlot:
            data.update({'solar': int(record.cv_address_sandlot)})
        if record.cv_address_nro_door:
            data.update({'numeroDePuerta': record.cv_address_nro_door})
        if record.cv_address_state_id:
            data.update({'deptoCod': int(record.cv_address_state_id.code)})
        else:
            data.update({'deptoCod': 99})
        return data

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            employee = self._context.get('employee')
            onsc_legajo_integration_error_WS6_1_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS6_1_9004")
            try:
                employee.write({'notify_sgh': False})
            except Exception as e:
                long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='WS6.1', type='error',
                                    integration_log=onsc_legajo_integration_error_WS6_1_9004,
                                    long_description=long_description)

    def _process_servicecall_error(self, exception, origin_name, integration_error, long_description=''):
        super(ONSCLegajoAbstractSyncWS6_1, self)._process_servicecall_error(exception, origin_name, integration_error,
                                                                            long_description)

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        IntegrationError = self.env['onsc.legajo.integration.error']
        if hasattr(response, 'codigo'):
            result_error_code = response.codigo
            error = IntegrationError.search([('integration_code', '=', integration_error.integration_code),
                                             ('code_error', '=', str(result_error_code))], limit=1)
            employee = self._context.get('employee')
            _long_description = 'Funcionario %s, %s' % (employee.display_name, response.mensaje)
            self.create_new_log(origin=origin_name, type='error', integration_log=error or integration_error,
                                ws_tuple=False, long_description=_long_description)

        else:
            long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."
            super(ONSCLegajoAbstractSyncWS6_1, self)._process_response_witherror(response,
                                                                                 origin_name,
                                                                                 integration_error,
                                                                                 long_description)
