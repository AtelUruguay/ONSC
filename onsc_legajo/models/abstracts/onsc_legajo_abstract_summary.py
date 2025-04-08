# -*- coding: utf-8 -*-

import datetime
import logging

from odoo import models, api, tools, fields
from zeep.helpers import serialize_object

_logger = logging.getLogger(__name__)


class ONSCLegajoAbstractSyncSummary(models.AbstractModel):
    _name = 'onsc.legajo.abstract.summary'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Modelo abstracto para la sincronización de legajo con sumarios'

    @api.model
    def syncronize(self, log_info=False, days=False, fecha_hasta=False, fecha_desde=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_summary')
        timeout = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_summary_TIMEOUT')
        tz_delta = self.env['ir.config_parameter'].sudo().get_param('server_timezone_delta')
        onsc_legajo_summary_Pclave = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_summary_Pclave')
        onsc_legajo_summary_Pmsuserid = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_summary_Pmsuserid')
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_summary_9005")

        wsclient = self._get_client(parameter, 'Sumario', integration_error, timeout=int(timeout), use_zeep=True)
        if not self._context.get('wizard'):
            paFechaDesde = self.env.user.company_id.summary_date_from
            pfFechaDesdewithTz = self.env.user.company_id.summary_date_from

            paFechaDesde += datetime.timedelta(hours=int(tz_delta))
        else:
            paFechaDesde = fecha_desde
            pfFechaDesdewithTz = fecha_desde

            paFechaDesde += datetime.timedelta(hours=int(tz_delta))

        if days == 0:
            days = 700

        if days and days > 0:
            paFechaHasta = paFechaDesde + datetime.timedelta(days=days)
            paFechaHastawithTz = pfFechaDesdewithTz + datetime.timedelta(days=days)
        elif fecha_hasta:
            if not self._context.get('wizard'):
                paFechaHasta = datetime.datetime.strptime(fecha_hasta, '%Y-%m-%d %H:%M:%S.%f')
                paFechaHasta -= datetime.timedelta(seconds=self.env.user.company_id.summary_latency_inseconds)
                paFechaHastawithTz = datetime.datetime.strptime(fecha_hasta, '%Y-%m-%d %H:%M:%S.%f')
            else:
                paFechaHasta = fecha_hasta
                paFechaHastawithTz = fecha_hasta
                paFechaHasta += datetime.timedelta(hours=int(tz_delta))
        else:
            paFechaHasta = fields.Datetime.now()
            paFechaHastawithTz = fields.Datetime.now()
            paFechaHasta += datetime.timedelta(hours=int(tz_delta))
            paFechaHasta -= datetime.timedelta(seconds=self.env.user.company_id.summary_latency_inseconds)
        if not self._context.get('wizard'):
            paFechaDesde -= datetime.timedelta(seconds=self.env.user.company_id.summary_latency_inseconds)
        data = {
            'Pmsuserid': onsc_legajo_summary_Pmsuserid,
            'Pclave': onsc_legajo_summary_Pclave,
            'Pfechahasta': paFechaDesde.strftime('%Y-%m-%d'),
            'Pcant_dias': days,
        }
        return self.with_context(
            log_info=log_info,
            simpleWsdl=True,
            date_from=pfFechaDesdewithTz,
            date_to=paFechaHastawithTz,
            use_execute_with_args=True).suspend_security()._syncronize(
            wsclient,
            parameter,
            'Sumario',
            integration_error,
            data)

    def _populate_from_syncronization(self, response):
        with self._cr.savepoint():
            onsc_legajo_integration_error_9004 = self.env.ref(
                "onsc_legajo.onsc_legajo_integration_error_summary_9004")
            try:
                self._populate_staging(serialize_object(response.Sdtinfosum).get('SDTInfoSumarios.SDTInfoSumariosItem'))
                self.env.user.company_id.sudo().write({
                    'summary_date_from': self.env.context.get('date_to')
                })
            except Exception as e:
                long_description = "Error: %s" % tools.ustr(e)
                _logger.warning(long_description)
                self.create_new_log(origin='Sumario', type='error',
                                    integration_log=onsc_legajo_integration_error_9004,
                                    long_description=long_description)

    def _populate_staging(self, response):
        Staging = self.env['onsc.legajo.summary'].suspend_security()
        tz_delta = self.env['ir.config_parameter'].sudo().get_param('server_timezone_delta')

        with self._cr.savepoint():
            try:
                response = sorted(response, key=lambda x: x['SumFchAct'])
                for operation in response:
                    vals = self._get_base_dict(operation, tz_delta)
                    staging = self._get_staging(vals)
                    if vals.get('state') == 'E' and staging:
                        staging.unlink()
                    elif staging and vals.get('state') != 'E':
                        vals['communications_ids'] = [(5,)] + vals['communications_ids']
                        staging.write(vals)
                    elif not staging and vals.get('state') != 'E':
                        Staging.create(vals)
            except Exception as e:
                raise e

    def _get_base_dict(self, operation, tz_delta):
        key = "%s-%s" % (operation.get('PerDocNum'), operation.get('SumNum'))
        vals = {
            'key': key,
            'summary_number': operation.get('SumNum'),
            'record_number': operation.get('SumExpNum'),
            'nro_doc': operation.get('PerDocNum'),
            'document_type': operation.get('DocTpoDsc'),
            'emissor_country': operation.get('PaiNom'),
            'inciso_code': int(operation.get('IncisoCod')) if operation.get('IncisoCod') else None,
            'inciso_name': operation.get('IncisoDescripcion'),
            'operating_unit_code': operation.get('UECod'),
            'operating_unit_name': operation.get('UEDsc'),
            'regime': operation.get('Regimen'),
            'relationship_date': operation.get('VinFchDes'),
            'state': operation.get('SumEst'),
            'summary_causal': operation.get('SumCauDsc'),
            'act_date': operation.get('SumFchAct'),
            'interrogator_notify_date': operation.get('SumFchNotSdo'),
            'summary_notify_date': operation.get('SumFchNotSte'),
            'penalty_type_id': self.env['onsc.legajo.penalty.type'].search(
                [('code', '=', operation.get('SanTipCod'))], limit=1).id if operation.get('SanTipCod') else False,
            'summary_detail': operation.get('SanTipDsc'),
            'instructor_name': operation.get('SumInsSumNomCompleto'),
            'instructor_email': operation.get('SumInsSumCorreo'),
            'suspension': operation.get('SumSusPreFlg', '').lower(),
            'retention_percentage': operation.get('HabRetTipDsc'),
            'instructor_doc_number': operation.get('SumInsSumDocumento'),
            'communications_ids': [
                (0, 0, {
                    'communication_date': com.get('SumComFchCre'),
                    'communication_type': com.get('ComSubTipTip'),
                    'instance': com.get('ComSubTipDsc')
                })
                for com in operation.get('SumarioComunicacion', {}).get('SumarioComunicacionItem', [])
            ]
        }
        if vals['suspension'] == 's':
            if isinstance(operation.get('SumSusPreFchDes'), str) and operation['SumSusPreFchDes'] != '1000-01-01':
                vals['start_date_suspension'] = fields.Date.to_date(
                    datetime.datetime.strptime(operation['SumSusPreFchDes'], '%d/%m/%Y').date())
            if isinstance(operation.get('SumSusPreFchHas'), str) and operation['SumSusPreFchHas'] != '1000-01-01':
                vals['end_date_suspension'] = fields.Date.to_date(
                    datetime.datetime.strptime(operation['SumSusPreFchHas'], '%d/%m/%Y').date())

        if operation.get('DocTpoDsc') == 'Cédula':
            vals['cv_document_type_id'] = self.env['onsc.cv.document.type'].search([('code', '=', 'ci')], limit=1).id
        if operation.get('PaiNom') == 'Uruguay':
            vals['country_id'] = self.env.ref('base.uy').id

        return vals

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

            super(ONSCLegajoAbstractSyncSummary, self)._process_response_witherror(response,
                                                                               origin_name,
                                                                               integration_error,
                                                                               long_description)

    def _get_staging(self, vals):
        Staging = self.env['onsc.legajo.summary'].suspend_security()
        return Staging.search([('key', '=', vals.get('key'))])
