# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, api, tools, fields, _

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncWS7(models.AbstractModel):
    _name = 'onsc.legajo.abstract.ws7'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con WS7'

    @api.model
    def syncronize(self, log_info=False, days=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS7_F_PU_RVE_MOVIMIENTOS')
        timeout = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS7_F_PU_RVE_MOVIMIENTOS_TIMEOUT')
        tz_delta = self.env['ir.config_parameter'].sudo().get_param('server_timezone_delta')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS7_9005")

        wsclient = self._get_client(parameter, 'WS7', integration_error, timeout=int(timeout))

        paFechaDesde = self.env.user.company_id.ws7_date_from
        pfFechaDesdewithTz = self.env.user.company_id.ws7_date_from

        paFechaDesde += datetime.timedelta(hours=int(tz_delta))

        if days and days > 0:
            paFechaHasta = paFechaDesde + datetime.timedelta(days=days)
            paFechaHastawithTz = pfFechaDesdewithTz + datetime.timedelta(days=days)
        else:
            paFechaHasta = fields.Datetime.now()
            paFechaHastawithTz = fields.Datetime.now()
            paFechaHasta -= datetime.timedelta(seconds=self.env.user.company_id.ws7_latency_inseconds)
            paFechaHastawithTz -= datetime.timedelta(seconds=self.env.user.company_id.ws7_latency_inseconds)
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
                self.env.user.company_id.sudo().write({
                    'ws7_date_from': self.env.context.get('date_to')
                })
                # response_test = []
                # for item in response:
                #     if item.mov == 'ASCENSO':
                #         response_test.append(item)

                # for operation in response:

                # if operation.mov in ['ALTA', 'BAJA']:
                #     self._check_movement(Contract,
                #                          operation,
                #                          onsc_legajo_integration_error_WS7_9004)
                # if operation.mov == 'ASCENSO' and operation.tipo_mov == 'BAJA':
                #     self.set_ascenso(Contract,
                #                      operation,
                #                      operation.mov,
                #                      response,
                #                      onsc_legajo_integration_error_WS7_9004)
                #     return True
                # if operation.mov == 'TRANSFORMA' and operation.tipo_mov == 'BAJA':
                #     self.set_transforma(Contract,
                #                         operation,
                #                         operation.mov,
                #                         response,
                #                         onsc_legajo_integration_error_WS7_9004)
                #     return True
                # if operation.mov == 'REESTRUCTURA' and operation.tipo_mov == 'BAJA':
                #     self.set_reestructura(Contract,
                #                           operation,
                #                           operation.mov,
                #                           response,
                #                           onsc_legajo_integration_error_WS7_9004)
                # return True

            except Exception as e:
                long_description = "Error: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='WS7', type='error',
                                    integration_log=onsc_legajo_integration_error_WS7_9004,
                                    long_description=long_description)

    def _populate_staging(self, response):
        Inciso = self.env['onsc.catalog.inciso'].suspend_security()
        OperatingUnit = self.env['operating.unit'].suspend_security()
        DocType = self.env['onsc.cv.document.type'].suspend_security()
        Country = self.env['res.country'].suspend_security()
        Race = self.env['onsc.cv.race'].suspend_security()
        IncomeMechanism = self.env['onsc.legajo.income.mechanism'].suspend_security()
        Regime = self.env['onsc.legajo.regime'].suspend_security()
        Descriptor1 = self.env['onsc.catalog.descriptor1'].suspend_security()
        Descriptor2 = self.env['onsc.catalog.descriptor2'].suspend_security()
        Descriptor3 = self.env['onsc.catalog.descriptor3'].suspend_security()
        Descriptor4 = self.env['onsc.catalog.descriptor4'].suspend_security()
        ExtinctionCommission = self.env['onsc.legajo.reason.extinction.commission'].suspend_security()
        Gender = self.env['onsc.cv.gender'].suspend_security()
        MaritalStatus = self.env['onsc.cv.status.civil'].suspend_security()
        Staging = self.env['onsc.legajo.staging.ws7'].suspend_security()
        stagings = self.env['onsc.legajo.staging.ws7']

        integration_error_WS7_9004 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS7_9004")

        with self._cr.savepoint():
            try:
                for operation in response:
                    if operation.primer_nombre == 'SIN DATO':
                        continue
                    logs_list = []

                    vals = self._get_base_dict(operation)
                    _is_op_unicity_valid = self._is_op_unicity_valid(vals, integration_error_WS7_9004)
                    if not _is_op_unicity_valid:
                        continue

                    is_simplify_record = vals.get('mov') in ['ALTA', 'BAJA']
                    # if not is_simplify_record:
                    #     inciso_id = self._get_catalog_id(Inciso, 'budget_code', operation, 'inciso', logs_list)
                    #     operating_unit_id = OperatingUnit.search([('budget_code', '=', str(operation.ue)),
                    #                                               ('inciso_id', '=', inciso_id)], limit=1).id
                    #     if not operating_unit_id:
                    #         logs_list.append(
                    #             _('No se encontró en el catálogo Unidad ejecutora el valor %s') % (operation.ue))
                    #
                    #     cv_document_type_id = self._get_catalog_id(DocType, 'code_other', operation, 'tipo_doc',
                    #                                                logs_list)
                    #     country_id = self._get_catalog_id(Country, 'code_rve', operation, 'cod_pais', logs_list)
                    #     race_id = self._get_catalog_id(Race, 'code', operation, 'raza', logs_list)
                    #     income_mechanism_id = self._get_catalog_id(IncomeMechanism, 'code', operation, 'cod_mecing',
                    #                                                logs_list)
                    #     descriptor1_id = self._get_catalog_id(Descriptor1, 'code', operation, 'cod_desc1', logs_list)
                    #     descriptor2_id = self._get_catalog_id(Descriptor2, 'code', operation, 'cod_desc2', logs_list)
                    #     descriptor3_id = self._get_catalog_id(Descriptor3, 'code', operation, 'cod_desc3', logs_list)
                    #     descriptor4_id = self._get_catalog_id(Descriptor4, 'code', operation, 'cod_desc4', logs_list)
                    #
                    #     extinction_commission_id = self._get_catalog_id(ExtinctionCommission, 'code', operation,
                    #                                                     'comi_mot_ext',
                    #                                                     logs_list)
                    #     gender_id = self._get_catalog_id(Gender, 'code', operation, 'sexo', logs_list)
                    #     marital_status_id = self._get_catalog_id(MaritalStatus, 'code', operation, 'codigoEstadoCivil',
                    #                                              logs_list)
                    #     regime_id = self._get_catalog_id(Regime, 'codRegimen', operation, 'cod_reg', logs_list)
                    #
                    #     vals.update({
                    #         'inciso_id': inciso_id,
                    #         'operating_unit_id': operating_unit_id,
                    #         'cv_document_type_id': cv_document_type_id,
                    #         'country_id': country_id,
                    #         'race_id': race_id,
                    #         'income_mechanism_id': income_mechanism_id,
                    #         'regime_id': regime_id,
                    #         'descriptor1_id': descriptor1_id,
                    #         'descriptor2_id': descriptor2_id,
                    #         'descriptor3_id': descriptor3_id,
                    #         'descriptor4_id': descriptor4_id,
                    #         'extinction_commission_id': extinction_commission_id,
                    #         'gender_id': gender_id,
                    #         'marital_status_id': marital_status_id,
                    #     })

                    if is_simplify_record:
                        vals.update({'state': 'na'})

                    stagings |= Staging.create(vals)
                stagings.button_in_process()
            except Exception as e:
                raise e

    def _get_base_dict(self, operation):
        mov = hasattr(operation, 'mov') and operation.mov or False
        fecha_aud = hasattr(operation, 'fecha_aud') and datetime.datetime.strptime(operation.fecha_aud,
                                                                                   '%Y-%m-%d %H:%M:%S.%f') or ''
        key = "%s-%s-%s-%s" % (fecha_aud, operation.doc, operation.mov, operation.tipo_mov)

        if hasattr(operation, 'fecha_vig'):
            fecha_vig = datetime.datetime.strptime(operation.fecha_vig, '%d/%m/%Y').date()
        else:
            fecha_vig = False
        if hasattr(operation, 'fechaGraduacion'):
            fechaGraduacion = datetime.datetime.strptime(operation.fechaGraduacion, '%d/%m/%Y').date()
        else:
            fechaGraduacion = False

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
            'cod_mecing': operation.cod_mecing if hasattr(operation, 'cod_mecing') else False,
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
        }

    def _get_catalog_id(self, Catalog, catalog_field, operation, operation_code, log_list):
        """
        Get the catalog ID based on the given operation code.
        :param Catalog: Env of Object. Ex: self.env['catalog']
        :param catalog_field: Field name of the catalog. Ex: 'code'
        :param operation: Record of the operation
        :param operation_code: Var name of the operation. Ex: 'tipo_doc'
        :param log_list: Log list to append errors
        :return: id or False
        """
        if not hasattr(operation, operation_code):
            return False
        int_valid_operation_value = isinstance(getattr(operation, operation_code), int)
        char_valid_operation_value = isinstance(getattr(operation, operation_code), str) and getattr(operation,
                                                                                                     operation_code) != ""
        if int_valid_operation_value or char_valid_operation_value:
            recordset = Catalog.search([(catalog_field, '=', getattr(operation, operation_code))], limit=1)
            if not recordset:
                log_list.append(_('No se encontró en el catálogo %s el valor %s') % (
                    Catalog._description, getattr(operation, operation_code)))
            return recordset.id
        return False

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
