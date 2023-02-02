# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools, _

from ...soap import soap_client

_logger = logging.getLogger(__name__)


class ONSCLegajoRegime(models.Model):
    _name = 'onsc.legajo.regime'
    _description = 'Régimen'

    codRegimen = fields.Char(string=u"Código régimen", required=True, index=True)
    descripcionRegimen = fields.Char(string=u"Descripción régimen", required=True)
    name = fields.Char(string="Nombre del régimen", compute='_compute_name', store=True)
    indVencimiento = fields.Boolean(string="Requiere indicar fecha de vencimiento")
    presupuesto = fields.Boolean(string="Presupuesto")
    vigente = fields.Boolean(string="Vigente")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('codRegimen_uniq', 'unique("codRegimen")', u'El código de régimen debe ser único'),
        ('descripcion_uniq', 'unique("descripcionRegimen")', u'La descripción de régimen debe ser única')
    ]

    @api.depends('codRegimen', 'descripcionRegimen')
    def _compute_name(self):
        for record in self:
            if record.codRegimen and record.descripcionRegimen:
                record.name = '%s - %s' % (record.codRegimen, record.descripcionRegimen)
            else:
                record.name = ''

    @api.model
    def syncronize(self):
        ONSCLegajoClient = soap_client.ONSCLegajoClient()
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS14_regimen')
        cron = self.env.ref("onsc_legajo.sync_legajo_regime")
        integration_error_WS14_9005 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9005")
        try:
            response = ONSCLegajoClient.get_response(parameter, {})
        except Exception as e:
            self.env.cr.rollback()
            self._create_log(
                origin=cron.name,
                type='error',
                integration_log=integration_error_WS14_9005,
                ws_tuple=False,
                long_description=tools.ustr(e))
            return
        if hasattr(response, 'servicioResultado'):
            if response.servicioResultado.codigo == 0:
                self._populate_from_syncronization(response)
            else:
                self._create_log(
                    origin=cron.name,
                    type='error',
                    integration_log=integration_error_WS14_9005,
                    ws_tuple=False,
                    long_description=tools.ustr(response.servicioResultado.mensaje))
        return True

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        all_odoo_regime = self.search([('active', 'in', [False, True])])
        all_odoo_regime_codeRegimen_list = all_odoo_regime.mapped('codRegimen')

        all_external_codRegimen_list = []
        cron = self.env.ref("onsc_legajo.sync_legajo_regime")
        integration_error_WS14_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9000")
        integration_error_WS14_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9001")
        integration_error_WS14_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9002")

        for external_record in response.listaRegimenPlaza:
            codRegimen_str = str(external_record.codRegimen)
            all_external_codRegimen_list.append(codRegimen_str)
            # CREANDO NUEVO ELEMENTO
            if codRegimen_str not in all_odoo_regime_codeRegimen_list:
                try:
                    self.create({
                        'codRegimen': codRegimen_str,
                        'descripcionRegimen': external_record.descripcionRegimen,
                        'indVencimiento': external_record.indVencimiento,
                        'presupuesto': external_record.presupuesto == 'S',
                        'vigente': external_record.vigente == 'S',
                    })
                    self._create_log(
                        origin=cron.name,
                        type='info',
                        integration_log=integration_error_WS14_9000,
                        ws_tuple=external_record,
                        long_description='Evento: Creación'
                    )
                except Exception as e:
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self._create_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS14_9001,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
            # MODIFICANDO ELEMENTO EXISTENTE
            else:
                try:
                    all_odoo_regime.filtered(lambda x: x.codRegimen == codRegimen_str).write({
                        'descripcionRegimen': external_record.descripcionRegimen,
                        'indVencimiento': external_record.indVencimiento,
                        'presupuesto': external_record.presupuesto,
                        'vigente': external_record.vigente,
                        'active': True,
                    })
                    self._create_log(
                        origin=cron.name,
                        type='info',
                        integration_log=integration_error_WS14_9000,
                        ws_tuple=external_record,
                        long_description='Evento: Actualización'
                    )
                except Exception as e:
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self._create_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS14_9002,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
        # DESACTIVANDO ELEMENTOS QUE NO VINIERON
        all_odoo_regime.filtered(lambda x: x.codRegimen not in all_odoo_regime_codeRegimen_list).write({
            'active': False
        })

    def _create_log(self, origin, type, integration_log, ws_tuple=False, long_description=False):
        if long_description and ws_tuple:
            _long_description = _('%s Tupla: %s') % (long_description, str(ws_tuple))
        elif not ws_tuple:
            _long_description = long_description
        else:
            _long_description = _('Tupla: %s') % (str(ws_tuple))
        return self.env['onsc.log'].create({
            'process': 'legajo',
            'origin': origin,
            'type': type,
            'ref': integration_log.integration_code,
            'code': integration_log.code_error,
            'description': integration_log.description,
            'long_description': _long_description
        })
