# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, api, tools, fields

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS7(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws7'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS7'

    @api.model
    def syncronize(self, log_info=False, days=False, fecha_hasta=False, fecha_desde=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS7_F_PU_RVE_MOVIMIENTOS')
        timeout = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS7_F_PU_RVE_MOVIMIENTOS_TIMEOUT')
        tz_delta = self.env['ir.config_parameter'].sudo().get_param('server_timezone_delta')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS7_9005")

        wsclient = self._get_client(parameter, 'WS7', integration_error, timeout=int(timeout))
        if not self._context.get('wizard'):
            paFechaDesde = self.env.user.company_id.ws7_date_from
            pfFechaDesdewithTz = self.env.user.company_id.ws7_date_from

            paFechaDesde += datetime.timedelta(hours=int(tz_delta))
        else:
            paFechaDesde = fecha_desde
            pfFechaDesdewithTz = fecha_desde

            paFechaDesde += datetime.timedelta(hours=int(tz_delta))

        if days and days > 0:
            paFechaHasta = paFechaDesde + datetime.timedelta(days=days)
            paFechaHastawithTz = pfFechaDesdewithTz + datetime.timedelta(days=days)
        elif fecha_hasta:
            if not self._context.get('wizard'):
                paFechaHasta = datetime.datetime.strptime(fecha_hasta, '%Y-%m-%d %H:%M:%S.%f')
                paFechaHasta -= datetime.timedelta(seconds=self.env.user.company_id.ws7_latency_inseconds)
                paFechaHastawithTz = datetime.datetime.strptime(fecha_hasta, '%Y-%m-%d %H:%M:%S.%f')
            else:
                paFechaHasta = fecha_hasta
                paFechaHastawithTz = fecha_hasta
                paFechaHasta += datetime.timedelta(hours=int(tz_delta))
        else:
            paFechaHasta = fields.Datetime.now()
            paFechaHastawithTz = fields.Datetime.now()
            paFechaHasta += datetime.timedelta(hours=int(tz_delta))
            paFechaHasta -= datetime.timedelta(seconds=self.env.user.company_id.ws7_latency_inseconds)
        if not self._context.get('wizard'):
            paFechaDesde -= datetime.timedelta(seconds=self.env.user.company_id.ws7_latency_inseconds)
        data = {
            'paFechaDesde': paFechaDesde.strftime('%d/%m/%Y %H:%M:%S'),
            'paFechaHasta': paFechaHasta.strftime('%d/%m/%Y %H:%M:%S'),
        }
        return self.with_context(
            log_info=log_info,
            simpleWsdl=True,
            date_from=pfFechaDesdewithTz,
            date_to=paFechaHastawithTz).suspend_security()._syncronize(
            wsclient,
            parameter,
            'WS7',
            integration_error,
            data)

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            onsc_legajo_integration_error_WS7_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS7_9004")
            try:
                self._populate_staging(response)
                if not self._context.get('wizard'):
                    self.env.user.company_id.sudo().write({
                        'ws7_date_from': self.env.context.get('date_to')
                    })
            except Exception as e:
                long_description = "Error: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='WS7', type='error',
                                    integration_log=onsc_legajo_integration_error_WS7_9004,
                                    long_description=long_description)

    def _populate_staging(self, response):
        Staging = self.env['onsc.legajo.staging.ws7'].suspend_security()
        stagings = self.env['onsc.legajo.staging.ws7']
        tz_delta = self.env['ir.config_parameter'].sudo().get_param('server_timezone_delta')

        integration_error_WS7_9004 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS7_9004")

        with self._cr.savepoint():
            try:
                for operation in response:
                    if operation.primer_nombre == 'SIN DATO':
                        continue
                    vals = self._get_base_dict(operation, tz_delta)
                    if not self._context.get('wizard'):
                        _is_op_unicity_valid = self._is_op_unicity_valid(vals, integration_error_WS7_9004)
                        if not _is_op_unicity_valid:
                            continue
                        is_simplify_record = vals.get('mov') in ['ALTA', 'BAJA', 'COMISION', 'CAMBIO_DEPTO']
                        if is_simplify_record:
                            vals.update({'state': 'na'})
                        stagings |= Staging.create(vals)

                    else:
                        staging = self._get_staging(vals)
                        if not staging:
                            is_simplify_record = vals.get('mov') in ['ALTA', 'BAJA', 'COMISION', 'CAMBIO_DEPTO']
                            if is_simplify_record:
                                vals.update({'state': 'na'})
                            stagings |= Staging.create(vals)
                        elif staging.state in ('error', 'in_process'):
                            vals.update({'state': 'in_process'})
                            staging.write(vals)
                            stagings |= staging
                        else:
                            continue
                stagings.button_in_process()
            except Exception as e:
                raise e

    def _get_base_dict(self, operation, tz_delta):
        mov = hasattr(operation, 'mov') and operation.mov or False
        fecha_aud = hasattr(operation, 'fecha_aud') and datetime.datetime.strptime(operation.fecha_aud,
                                                                                   '%Y-%m-%d %H:%M:%S.%f') or ''
        key = "%s-%s-%s-%s" % (fecha_aud, operation.doc, operation.mov, operation.tipo_mov)
        fecha_aud += datetime.timedelta(hours=int(tz_delta) * -1)

        if hasattr(operation, 'fecha_vig'):
            fecha_vig = datetime.datetime.strptime(operation.fecha_vig, '%d/%m/%Y').date()
        else:
            fecha_vig = False
        if hasattr(operation, 'fechaGraduacion'):
            fechaGraduacion = datetime.datetime.strptime(operation.fechaGraduacion, '%d/%m/%Y').date()
        else:
            fechaGraduacion = False

        if hasattr(operation, 'fechaVencimientoContrato'):
            fechaVencimientoContrato = datetime.datetime.strptime(operation.fechaVencimientoContrato, '%d/%m/%Y').date()
        else:
            fechaVencimientoContrato = False


        return {
            'info_income': str(operation),
            'doc': operation.doc,
            'key': key,
            'primer_nombre': operation.primer_nombre,
            'segundo_nombre': operation.segundo_nombre if hasattr(operation, 'segundo_nombre') else False,
            'primer_ap': operation.primer_ap,
            'segundo_ap': operation.segundo_ap if hasattr(operation, 'segundo_ap') else False,
            'fecha_nac': datetime.datetime.strptime(operation.fecha_nac, '%d/%m/%Y').date(),
            'fecha_ing_adm': datetime.datetime.strptime(operation.fecha_ing_adm,
                                                        '%d/%m/%Y').date(),
            'cod_mot_baja': operation.cod_mot_baja if hasattr(operation, 'cod_mot_baja') else False,
            'fecha_vig': fecha_vig,
            'fecha_aud': fecha_aud,
            'mov': mov,
            'tipo_mov': operation.tipo_mov,
            'pdaId': operation.pdaId,
            'movimientoPadreId': operation.movimientoPadreId if hasattr(operation, 'movimientoPadreId') else False,
            'fecha_desde_vinc': operation.fecha_desde_vinc if hasattr(operation, 'fecha_desde_vinc') else False,
            'idPuesto': operation.idPuesto,
            'nroPlaza': operation.nroPlaza,
            'secPlaza': operation.secPlaza,
            'programa': operation.programa if hasattr(operation, 'programa') else False,
            'proyecto': operation.proyecto if hasattr(operation, 'proyecto') else False,
            'aniosInactividad': operation.aniosInactividad if hasattr(operation, 'aniosInactividad') else False,
            'fechaGraduacion': fechaGraduacion,
            'inciso': operation.inciso if hasattr(operation, 'inciso') else False,
            'ue': operation.ue if hasattr(operation, 'ue') else False,
            'tipo_doc': operation.tipo_doc,
            'cod_pais': operation.cod_pais,
            'raza': operation.raza if hasattr(operation, 'raza') else False,
            'cod_desc1': operation.cod_desc1 if hasattr(operation, 'cod_desc1') else False,
            'cod_desc2': operation.cod_desc2 if hasattr(operation, 'cod_desc2') else False,
            'cod_desc3': operation.cod_desc3 if hasattr(operation, 'cod_desc3') else False,
            'cod_desc4': operation.cod_desc4 if hasattr(operation, 'cod_desc4') else False,
            'comi_inciso_dest': operation.comi_inciso_dest if hasattr(operation, 'comi_inciso_dest') else False,
            'comi_ue_dest': operation.comi_ue_dest if hasattr(operation, 'comi_ue_dest') else False,
            'comi_mot_ext': operation.comi_mot_ext if hasattr(operation, 'comi_mot_ext') else False,
            'comi_reg': operation.comi_reg if hasattr(operation, 'comi_reg') else False,
            'jornada_ret': operation.jornada_ret if hasattr(operation, 'jornada_ret') else False,
            'sexo': operation.sexo if hasattr(operation, 'sexo') else False,
            'codigoEstadoCivil': operation.codigoEstadoCivil if hasattr(operation, 'codigoEstadoCivil') else False,
            'cod_reg': operation.cod_reg if hasattr(operation, 'cod_reg') else False,
            'contract_expiration_date':fechaVencimientoContrato
        }

    def _is_op_unicity_valid(self, vals, onsc_legajo_integration_error_WS7_9004):
        Staging = self.env['onsc.legajo.staging.ws7'].suspend_security()
        if Staging.search_count([('key', '=', vals.get('key'))]):
            long_description = "Combinación de llave ya existente: %s" % vals.get('key')
            _logger.warning(long_description)
            self.create_new_log(origin='WS7', type='error',
                                integration_log=onsc_legajo_integration_error_WS7_9004,
                                long_description=long_description)
            return False
        return True

    def _process_response_witherror(self, response, origin_name, integration_error, long_description=''):
        IntegrationError = self.env['onsc.legajo.integration.error']
        if hasattr(response, 'codigo'):
            result_error_code = response.codigo
            error = IntegrationError.search([('integration_code', '=', integration_error.integration_code),
                                             ('code_error', '=', str(result_error_code))], limit=1)
            self.create_new_log(origin=origin_name, type='error', integration_log=error or integration_error,
                                ws_tuple=False, long_description=response.mensaje)

        else:
            long_description = "No se pudo conectar con el servicio web. Verifique la configuración o consulte con el administrador."

            super(ONSCLegajoAbstractSyncWS7, self)._process_response_witherror(response,
                                                                               origin_name,
                                                                               integration_error,
                                                                               long_description)

    def _get_staging(self, vals):
        Staging = self.env['onsc.legajo.staging.ws7'].suspend_security()
        return Staging.search([('key', '=', vals.get('key'))])
