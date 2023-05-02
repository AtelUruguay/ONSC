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
        """<inciso>2</inciso>
			 <ue>11</ue>
			 <!--Optional:-->
			 <descripcion>prueba WS</descripcion>
			 <presupuestales>S</presupuestales>
			 <!--1 or more repetitions:-->
			 <altaDetalle>
				 <fechaAlta>01/10/2022</fechaAlta>
				 <cedula>4437944</cedula>
				 <digitoVerificador>3</digitoVerificador>
				 <!--Optional:-->
				 <primerApellido>KLEEFELD</primerApellido>
				 <!--Optional:-->
				 <segundoApellido>PRIUS</segundoApellido>
				 <!--Optional:-->
				 <primerNombre>ALBA</primerNombre>
				 <!--Optional:-->
				 <segundoNombre>IRENE</segundoNombre>
				 <!--Optional:-->
				 <codRegimen>1007</codRegimen>
				 <!--Optional:-->
				 <codPartida>1221</codPartida>
				 <!--Optional:-->
				 <nroPuesto>74601</nroPuesto>
				 <!--Optional:-->
				 <nroPlaza>160</nroPlaza>
				 <!--Optional:-->
				 <programa>282</programa>
				 <!--Optional:-->
				 <proyecto>0</proyecto>
				 <!--Optional:-->
				 <descripcionMotivo>CGN ALTA YEYT MAYO 2022</descripcionMotivo>
				 <numeroNorma>18719</numeroNorma>
				 <articuloNorma>51</articuloNorma>
				 <tipoNormaSigla>L</tipoNormaSigla>
				 <anioNorma>2010</anioNorma>
				 <descripcionResolucion>CGN ALTA YEYT MAYO 2022</descripcionResolucion>
				 <fechaResolucion>27/05/2022</fechaResolucion>
				 <tipoResolucion>P</tipoResolucion>
				 <!--Optional:-->
				 <codigoEstadoCivil>1</codigoEstadoCivil>
				 <!--Optional:-->
				 <fechaDeNacimiento>06/09/1979</fechaDeNacimiento>
				 <sexo>M</sexo>
				 <!--Optional:-->
				 <lugarDeNacimiento>SAN JOSE</lugarDeNacimiento>
				 <!--Optional:-->
				 <tipoCiudadania>N</tipoCiudadania>
				 <!--Optional:-->
				 <nacionalidad>URUGUAYA</nacionalidad>
				 <!--Optional:-->
				 <serieCredencial>OBA</serieCredencial>
				 <!--Optional:-->
				 <numeroCredencial>6868</numeroCredencial>
				 <!--Optional:-->
				 <telefonoAlternativo>232342</telefonoAlternativo>
				 <!--Optional:-->
				 <telefonoMovil>099795454</telefonoMovil>
				 <!--Optional:-->
				 <eMail>mccampot@gmail.com</eMail>
				 <!--Optional:-->
				 <deptoCod>10</deptoCod>
				 <!--Optional:-->
				 <localidadCod>0</localidadCod>
				 <!--Optional:-->
				 <calleCod>842741</calleCod>
				 <!--Optional:-->
				 <numeroDePuerta>2803</numeroDePuerta>
				 <!--Optional:-->
				 <callCodEntre1>843582</callCodEntre1>
				 <!--Optional:-->
				 <callCodEntre2>842806</callCodEntre2>
				 <!--Optional:-->
				 <bis>0</bis>
				 <!--Optional:-->
				 <apto>204</apto>
				 <!--Optional:-->
				 <paraje>fdfdfdd</paraje>
				 <!--Optional:-->
				 <codigoPostal>1111</codigoPostal>
				 <!--Optional:-->
				 <manzana>1</manzana>
				 <!--Optional:-->
				 <solar>1</solar>
				 <!--Optional:-->
				 <mutuCod>3</mutuCod
				 <!--Optional:-->
				 <fechaDeIngresoAlaAdm>01/01/2014</fechaDeIngresoAlaAdm>
				 <!--Optional:-->
				 <aniosInactividad>0</aniosInactividad>
				 <!--Optional:-->
				 <!--Optional:-->
				 <responsableUO>1</responsableUO>
				 <!--Optional:-->
				 <codigoOcupacion>1</codigoOcupacion>
		</altaDetalle>"""

        data = {
            'inciso': record.inciso_id.budget_code or '0',
            'ue': record.operating_unit_id.budget_code or '0',
            'descripcion': record.description or '',
            'presupuestales': 'S',
            'altaDetalle': [
                {'fechaAlta': '01/10/2022',
                 'cedula': '4437944',
                 'digitoVerificador': '3',
                 'primerApellido': 'KLEEFELD',
                 'segundoApellido': 'PRIUS',
                 'primerNombre': 'ALBA',
                 'segundoNombre': 'IRENE',
                 'codRegimen': '1007',
                 'codPartida': '1221',
                 'nroPuesto': '74601',
                 'nroPlaza': '160',
                 'programa': '282',
                 'proyecto': '0',
                 'descripcionMotivo': 'CGN ALTA YEYT MAYO 2022',
                 'numeroNorma': '18719',
                 'articuloNorma': '51',
                 'tipoNormaSigla': 'L',
                 'anioNorma': '2010',
                 'descripcionResolucion': 'CGN ALTA YEYT MAYO 2022',
                 'fechaResolucion': '27/05/2022',
                 'tipoResolucion': 'P',
                 'codigoEstadoCivil': '1',
                 'fechaDeNacimiento': '06/09/1979',
                 'sexo': 'M',
                 'lugarDeNacimiento': 'SAN JOSE',
                 'tipoCiudadania': 'N',
                 'nacionalidad': 'URUGUAYA',
                 'serieCredencial': 'OBA',
                 'numeroCredencial': '6868',
                 'telefonoAlternativo': '232342',
                 'telefonoMovil': '099795454',
                 'eMail': 'mccampot@gmail.com',
                 'deptoCod': '10',
                 'localidadCod': '0',
                 'calleCod': '842741',
                 'numeroDePuerta': '2803',
                 'callCodEntre1': '843582',
                 'callCodEntre2': '842806',
                 'bis': '0',
                 'apto': '204',
                 'paraje': 'fdfdfdd',
                 'codigoPostal': '1111',
                 'manzana': '1',
                 'solar': '1',
                 'mutuCod': '3',
                 'fechaDeIngresoAlaAdm': '01/01/2014',
                 'aniosInactividad': '0',
                 'responsableUO': '1',
                 'codigoOcupacion': '1',
                 }]
        }
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
            vacante_ids = [(5,)]
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
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin='',
                            type='error',
                            integration_log=integration_error_WS14_9001,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
                        return "Error al sincronizar vacantes"

            else:
                return "No se encontraron vacantes"
            return vacante_ids
