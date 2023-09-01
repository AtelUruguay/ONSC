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
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS7_F_PU_RVE_MOVIMIENTOS')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS7_9005")
        wsclient = self._get_client(parameter, 'WS7', integration_error)
        data = {
            'paFechaDesde': '06/05/2022 00:00:00',
            'paFechaHasta': '08/05/2022 00:00:00'
        }
        return self.with_context(log_info=log_info, simpleWsdl=True).suspend_security()._syncronize(
            wsclient,
            parameter,
            'WS7',
            integration_error,
            data)

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            onsc_legajo_integration_error_WS7_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_WS7_9004")
            Contract = self.env['hr.contract'].sudo()
            try:
                self._populate_staging(response)
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
                long_description = "Error devuelto por SGH: %s" % tools.ustr(e)
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
        CommissionRegime = self.env['onsc.legajo.commission.regime'].suspend_security()
        RetributiveDay = self.env['onsc.legajo.jornada.retributiva'].suspend_security()
        Office = self.env['onsc.legajo.office'].suspend_security()
        Gender = self.env['onsc.cv.gender'].suspend_security()
        MaritalStatus = self.env['onsc.cv.status.civil'].suspend_security()

        Staging = self.env['onsc.legajo.staging.ws7'].suspend_security()

        for operation in response:
            vals = {
                'primer_nombre': operation.primer_nombre,
                'segundo_nombre': hasattr(operation, 'segundo_nombre') and operation.segundo_nombre or False,
                'primer_ap': operation.primer_ap,
                'segundo_ap': hasattr(operation, 'segundo_ap') and operation.segundo_ap or False,
                'fecha_nac': datetime.datetime.strptime(operation.fecha_nac, '%d/%m/%Y').date(),
                'fecha_ing_adm': datetime.datetime.strptime(operation.fecha_ing_adm,
                                                            '%d/%m/%Y').date(),
                'cod_mot_baja': hasattr(operation, 'cod_mot_baja') and operation.cod_mot_baja or False,
                'fecha_vig': hasattr(operation, 'fecha_vig') and datetime.datetime.strptime(operation.fecha_vig,
                                                                                            '%d/%m/%Y').date() or False,
                'fecha_aud': hasattr(operation, 'fecha_aud') and datetime.datetime.strptime(operation.fecha_aud,
                                                                                            '%d/%m/%Y').date() or False,
                'mov': hasattr(operation, 'mov') and operation.mov or False,
                'tipo_mov': hasattr(operation, 'tipo_mov') and operation.tipo_mov or False,
                'pdaId': hasattr(operation, 'pdaId') and operation.pdaId or False,
                'movimientoPadreId': hasattr(operation, 'proyecto') and operation.proyecto or False,
                'fecha_desde_vinc': hasattr(operation, 'fecha_desde_vinc') and operation.fecha_desde_vinc or False,
                'idPuesto': hasattr(operation, 'idPuesto') and operation.idPuesto or False,
                'nroPlaza': hasattr(operation, 'nroPlaza') and operation.nroPlaza or False,
                'secPlaza': hasattr(operation, 'secPlaza') and operation.secPlaza or False,
                'programa': hasattr(operation, 'programa') and operation.programa or False,
                'proyecto': hasattr(operation, 'proyecto') and operation.proyecto or False,
                'aniosInactividad': hasattr(operation, 'aniosInactividad') and operation.aniosInactividad or False,
                'fechaGraduacion': hasattr(operation, 'fechaGraduacion') and datetime.datetime.strptime(
                    operation.fechaGraduacion, '%d/%m/%Y').date() or False,

                'inciso_id': Inciso.search([('budget_code', '=', str(operation.inciso))], limit=1).id,
                'operating_unit_id': OperatingUnit.search([('budget_code', '=', str(operation.ue))], limit=1).id,
                'cv_document_type_id': DocType.search([('code', '=', str(operation.tipo_doc))], limit=1).id,
                'country_id': Country.search([('code', '=', str(operation.cod_pais))], limit=1).id,
                'race_id': hasattr(operation, 'raza') and Race.search([('code', '=', operation.raza)], limit=1).id,
                'income_mechanism_id': hasattr(operation, 'cod_mecing') and IncomeMechanism.search(
                    [('code', '=', operation.cod_mecing)], limit=1).id or False,
                'regime_id': hasattr(operation, 'cod_reg') and Regime.search([('codRegimen', '=', operation.cod_reg)],
                                                                             limit=1).id or False,
                'descriptor1_id': hasattr(operation, 'cod_desc1') and Descriptor1.search(
                    [('code', '=', operation.cod_desc1)], limit=1).id or False,
                'descriptor2_id': hasattr(operation, 'cod_desc2') and Descriptor2.search(
                    [('code', '=', operation.cod_desc2)], limit=1).id or False,
                'descriptor3_id': hasattr(operation, 'cod_desc3') and Descriptor3.search(
                    [('code', '=', operation.cod_desc3)], limit=1).id or False,
                'descriptor4_id': hasattr(operation, 'cod_desc4') and Descriptor4.search(
                    [('code', '=', operation.cod_desc4)], limit=1).id or False,
                'comision_inciso_dest_id': hasattr(operation, 'comi_inciso_dest') and Inciso.search(
                    [('budget_code', '=', str(operation.comi_inciso_dest))], limit=1).id or False,
                'comision_operating_unit_dest_id': hasattr(operation, 'comi_ue_dest') and OperatingUnit.search(
                    [('budget_code', '=', str(operation.comi_ue_dest))],
                    limit=1).id or False,
                'extinction_commission_id': hasattr(operation, 'comi_mot_ext') and ExtinctionCommission.search(
                    [('code', '=', operation.comi_mot_ext)],
                    limit=1).id or False,
                'commission_regime_id': hasattr(operation, 'comi_reg') and CommissionRegime.search(
                    [('code', '=', operation.comi_reg)], limit=1).id or False,
                'retributive_day_id': hasattr(operation, 'jornada_ret') and RetributiveDay.search(
                    [('code', '=', operation.jornada_ret)], limit=1).id or False,
                'gender_id': hasattr(operation, 'sexo') and Gender.search([('code', '=', operation.sexo)],
                                                                          limit=1).id or False,
                'marital_status_id': hasattr(operation, 'codigoEstadoCivil') and MaritalStatus.search(
                    [('code', '=', operation.codigoEstadoCivil)], limit=1).id or False,
            }
            Staging.create(vals)

    def _check_movement(self, Contract, operation, error):
        """
        Chequea que el movimiento exista en el sistema
        :param Contract: Recomendado: self.env['hr.contract'].sudo()
        :param operation: Recordset de la operacion
        :param error: Recordset del log de error
        """
        exist_contract = self._get_simple_contract(
            Contract,
            operation,
            use_search_count=True
        )
        if not exist_contract:
            self.create_new_log(
                origin='WS7',
                type='error',
                integration_log=error,
                ws_tuple=str(operation),
                long_description='Movimiento no encontrado en el sistema')

    def set_ascenso(self, Contract, operation, movement, response, error):
        second_movement = self._get_second_movement(operation, response, 'ALTA')
        # ---------------------FIXME ajustes manuales a la info del reuqest para poder testear
        operation.doc = '39893218'
        operation.inciso = '2'
        operation.ue = '8'

        second_movement.doc = '39893218'
        second_movement.inciso = '2'
        second_movement.ue = '8'
        # ---------------------FIXME

        if not second_movement:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Segundo movimiento no encontrado')
            return
        contract = self._get_contract(Contract, operation, legajo_state_operator='!=', legajo_state='baja')
        if len(contract) == 0:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Alta no encontrada')
        else:
            ascenso_causes_discharge = self.env.user.company_id.ws7_ascenso_causes_discharge_id
            contract_date_end = datetime.datetime.strptime(operation.fecha_vig, "%d/%m/%Y").date()
            contract.deactivate_legajo_contract(contract_date_end + datetime.timedelta(days=-1))

            new_contract = self._get_contract_copy(contract, second_movement, error)
            contract.write({
                'causes_discharge_id': ascenso_causes_discharge.id,
                'cs_contract_id': new_contract.id
            })

    def set_transforma(self, Contract, operation, movement, response, error):
        second_movement = self._get_second_movement(operation, response, 'ALTA')
        # ---------------------FIXME ajustes manuales a la info del reuqest para poder testear
        operation.doc = '39893218'
        operation.inciso = '2'
        operation.ue = '8'

        second_movement.doc = '39893218'
        second_movement.inciso = '2'
        second_movement.ue = '8'
        # ---------------------FIXME

        if not second_movement:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Segundo movimiento no encontrado')
            return
        contract = self._get_contract(Contract, operation, legajo_state_operator='!=', legajo_state='baja')
        if len(contract) == 0:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Alta no encontrada')
        else:
            transforma_causes_discharge_id = self.env.user.company_id.ws7_transforma_causes_discharge_id
            contract_date_end = datetime.datetime.strptime(operation.fecha_vig, "%d/%m/%Y").date()
            contract.deactivate_legajo_contract(contract_date_end + datetime.timedelta(days=-1))

            new_contract = self._get_contract_copy(contract, second_movement, error)
            contract.write({
                'causes_discharge_id': transforma_causes_discharge_id.id,
                'cs_contract_id': new_contract.id
            })

    def set_reestructura(self, Contract, operation, movement, response, error):
        second_movement = self._get_second_movement(operation, response, 'ALTA')
        # ---------------------FIXME ajustes manuales a la info del reuqest para poder testear
        operation.doc = '39893218'
        operation.inciso = '2'
        operation.ue = '8'

        second_movement.doc = '39893218'
        second_movement.inciso = '2'
        second_movement.ue = '8'
        # ---------------------FIXME

        if not second_movement:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Segundo movimiento no encontrado')
            return
        contract = self._get_contract(Contract, operation, legajo_state_operator='!=', legajo_state='baja')
        if len(contract) == 0:
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description='Alta no encontrada')
        else:
            causes_discharge_id = self.env.user.company_id.ws7_reestructura_causes_discharge_id
            contract_date_end = datetime.datetime.strptime(operation.fecha_vig, "%d/%m/%Y").date()
            contract.deactivate_legajo_contract(contract_date_end + datetime.timedelta(days=-1))

            new_contract = self._get_contract_copy(contract, second_movement, error)
            contract.write({
                'causes_discharge_id': causes_discharge_id.id,
                'cs_contract_id': new_contract.id
            })

    def _get_second_movement(self, operation, response, tipo_mov):
        """
        Retorna movimiento de contrapartida de la lista de movimientos devueltos por el WS
        :param operation: Recordset de la operacion
        :param response: Listado de recordsets devueltos por el WS
        :param tipo_mov: Tipo de movimiento contra el que se compara
        :return: Recordset secundario O False

        # TODO
        other_movement.idPuesto == operation.idPuesto and \
                    other_movement.nroPlaza == operation.nroPlaza and \
                    other_movement.secPlaza == operation.secPlaza and \
        """
        second_movement = False
        for other_movement in response:
            if other_movement.inciso == operation.inciso and \
                    other_movement.ue == operation.ue and \
                    other_movement.doc == operation.doc and \
                    other_movement.mov == operation.mov and \
                    other_movement.tipo_mov == tipo_mov:
                second_movement = other_movement
                break
        return second_movement

    def _get_simple_contract(self, Contract, operation, use_search_count=False):
        """
        Retorna contrato que cumple con los parametros de busqueda del movimiento
        :param Contract: Recomendado: self.env['hr.contract'].sudo()
        :param operation: Recordset de la operacion
        :param legajo_state_operator: Operador para buscar por estado de legajo
        :param legajo_state: Estado de legajo deseado
        :param use_search_count: True si se desea usar search_count  y no search
        :return Contract: Recordset o si el Contrato fue encontrado

        # TODO
        # ('emissor_country_id.code_rve', '=', str(operation.cod_pais)),
        # ('document_type_id.code', '=', str(tipo_doc)),

        no coincide con lo que estamos manejando
        """
        args = [
            ('position', '=', str(operation.idPuesto)),
            ('workplace', '=', operation.nroPlaza),
            ('sec_position', '=', operation.secPlaza),
            #
            ('nro_doc', '=', str(operation.doc)),
        ]
        if use_search_count:
            return Contract.search_count(args)
        return Contract.search(args, limit=1)

    def _get_contract(self, Contract, operation, legajo_state_operator, legajo_state, use_search_count=False):
        """
        Retorna contrato que cumple con los parametros de busqueda del movimiento
        :param Contract: Recomendado: self.env['hr.contract'].sudo()
        :param operation: Recordset de la operacion
        :param legajo_state_operator: Operador para buscar por estado de legajo
        :param legajo_state: Estado de legajo deseado
        :param use_search_count: True si se desea usar search_count  y no search
        :return Contract: Recordset o si el Contrato fue encontrado

        # TODO
        # ('emissor_country_id.code_rve', '=', str(operation.cod_pais)),
        # ('document_type_id.code', '=', str(tipo_doc)),

        no coincide con lo que estamos manejando
        """
        args = [
            ('inciso_id.budget_code', '=', str(operation.inciso)),  #
            ('operating_unit_id.budget_code', '=', str(operation.ue)),  #
            ('position', '=', str(operation.idPuesto)),
            ('workplace', '=', operation.nroPlaza),
            ('sec_position', '=', operation.secPlaza),
            #
            ('nro_doc', '=', str(operation.doc)),
            ('legajo_state', legajo_state_operator, legajo_state)  #
        ]
        if use_search_count:
            return Contract.search_count(args)
        return Contract.search(args, limit=1)

    def _get_contract_copy(self, contract, operation, error):
        """
        Duplica el contrato aplicando los cambios de la operacion
        :param contract: Recordset de contrato
        :param operation: Recordset de la operacion
        :param error: Recordset del log de error
        :return: Recordset de contrato

        # TODO
        si no estan todos los descriptores?
        de todos los juegos cuales pasamos? ej:
        cod_reg : hay que verificarlo?
        inciso?
        ue?
        """
        inciso = self.env['onsc.catalog.inciso'].search([('budget_code', '=', operation.inciso)], limit=1)
        operating_unit = self.env['operating.unit'].search([
            ('budget_code', '=', operation.ue),
            ('inciso_id', '=', inciso.id),
        ], limit=1)
        descriptor1 = self.env['onsc.catalog.descriptor1'].search([('code', '=', operation.cod_desc1)], limit=1)
        descriptor2 = self.env['onsc.catalog.descriptor2'].search([('code', '=', operation.cod_desc2)], limit=1)
        descriptor3 = self.env['onsc.catalog.descriptor3'].search([('code', '=', operation.cod_desc3)], limit=1)
        descriptor4 = self.env['onsc.catalog.descriptor4'].search([('code', '=', operation.cod_desc4)], limit=1)
        income_mechanism = self.env['onsc.legajo.income.mechanism'].search([('code', '=', operation.cod_mecing)],
                                                                           limit=1)
        regime = self.env['onsc.legajo.regime'].search([('codRegimen', '=', operation.cod_reg)], limit=1)

        if (descriptor1 and descriptor2 and descriptor3 and descriptor4 and income_mechanism and regime) is False:
            long_description = 'Algún catálogo de esta tupla no fué identificado: ' \
                               'Desc1: %s, Desc2: %s, Desc3: %s, Desc4: %s, Mec. Ing: %s, Regimen: %s' % (
                                   descriptor1.code,
                                   descriptor2.code,
                                   descriptor3.code,
                                   descriptor4.code,
                                   income_mechanism.code,
                                   regime.codRegimen,
                               )
            self.create_new_log(origin='WS7',
                                type='error',
                                integration_log=error,
                                ws_tuple=str(operation),
                                long_description=long_description)
        else:
            contract_date_end = datetime.datetime.strptime(operation.fecha_vig, "%d/%m/%Y").date()
            new_contract = contract.copy({
                'inciso_id': inciso.id,
                'operating_unit_id': operating_unit.id,
                'date_start': contract_date_end,
                'eff_date': contract_date_end,
                'date_end': False,
                'legajo_state': 'active',
                'descriptor1_id': descriptor1.id,
                'descriptor2_id': descriptor2.id,
                'descriptor3_id': descriptor3.id,
                'descriptor4_id': descriptor4.id,
                'income_mechanism_id': income_mechanism.id,
                'regime_id': regime.id,
                'position': str(operation.idPuesto),
                'workplace': str(operation.nroPlaza),
                'sec_position': str(operation.secPlaza),
                'program': str(operation.programa),
                'project': str(operation.proyecto),
            })
            return new_contract

    def _copy_jobs(self, source_contract, target_contract, operation):
        """
        :param source_contract: Recordset de contrato
        :param target_contract: Recordset de contrato
        :param operation: Recordset de la operacion
        :return: Nuevos puestos
        """
        if target_contract.operating_unit_id != source_contract.operating_unit_id:
            return self.env['hr.job']
        return source_contract.job_ids.copy({
            'contract_id': target_contract.id
        })

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
