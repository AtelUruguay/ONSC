# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoRegime(models.Model):
    _name = 'onsc.legajo.regime'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Régimen'

    codRegimen = fields.Char(string=u"Código régimen", required=True, index=True)
    descripcionRegimen = fields.Char(string=u"Descripción régimen", required=True)
    name = fields.Char(string="Nombre del régimen", compute='_compute_name', store=True)
    indVencimiento = fields.Boolean(string="Requiere indicar fecha de vencimiento")
    presupuesto = fields.Boolean(string="Presupuesto")
    vigente = fields.Boolean(string="Vigente")
    active = fields.Boolean(string="Activo", default=True)

    is_public_employee = fields.Boolean(string='Funcionario público')
    is_manager = fields.Boolean(string='Responsable UO')
    is_legajo = fields.Boolean(string='Legajo')
    is_fac2ac = fields.Boolean(string='Utilizar en comisiones FAC-AC')

    _sql_constraints = [
        ('codRegimen_uniq', 'unique("codRegimen")', u'El código de régimen debe ser único'),
        ('descripcion_uniq', 'unique("descripcionRegimen")', u'La descripción de régimen debe ser única')
    ]

    @api.constrains("is_fac2ac")
    def _check_is_fac2ac(self):
        for record in self:
            if record.is_fac2ac and self.search_count([('id', '!=', record.id), ('is_fac2ac', '=', True)]):
                raise ValidationError(_("Ya existe otro Régimen con el check 'Utilizar en comisiones FAC-AC' marcado"))

    @api.depends('codRegimen', 'descripcionRegimen')
    def _compute_name(self):
        for record in self:
            if record.codRegimen and record.descripcionRegimen:
                record.name = '%s - %s' % (record.codRegimen, record.descripcionRegimen)
            else:
                record.name = ''

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS14_regimen')
        cron = self.env.ref("onsc_legajo.sync_legajo_regime")
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")
        wsclient = self._get_client(parameter, cron.name, integration_error)
        return self.with_context(log_info=log_info).suspend_security()._syncronize(wsclient, parameter, cron.name,
                                                                                   integration_error, {})

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        all_odoo_recordsets = self.search([('active', 'in', [False, True])])
        all_odoo_recordsets_key_list = all_odoo_recordsets.mapped('codRegimen')

        all_external_ley_list = []
        cron = self.env.ref("onsc_legajo.sync_legajo_regime")
        integration_error_WS14_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9000")
        integration_error_WS14_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9001")
        integration_error_WS14_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS14_9002")

        with self._cr.savepoint():
            for external_record in response.listaRegimenPlaza:
                key_str = str(external_record.codRegimen)
                all_external_ley_list.append(key_str)

                vals = self._prepare_values(external_record)
                # CREANDO NUEVO ELEMENTO
                if key_str not in all_odoo_recordsets_key_list:
                    try:
                        # with self._cr.savepoint():
                        vals['codRegimen'] = key_str
                        self.create(vals)
                        if self._context.get('log_info'):
                            self.create_new_log(
                                origin=cron.name,
                                type='info',
                                integration_log=integration_error_WS14_9000,
                                ws_tuple=external_record,
                                long_description='Evento: Creación'
                            )
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin=cron.name,
                            type='error',
                            integration_log=integration_error_WS14_9001,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
                # MODIFICANDO ELEMENTO EXISTENTE
                else:
                    try:
                        all_odoo_recordsets.filtered(lambda x: x.codRegimen == key_str).write(vals)
                        if self._context.get('log_info'):
                            self.create_new_log(
                                origin=cron.name,
                                type='info',
                                integration_log=integration_error_WS14_9000,
                                ws_tuple=external_record,
                                long_description='Evento: Actualización'
                            )
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin=cron.name,
                            type='error',
                            integration_log=integration_error_WS14_9002,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
            # DESACTIVANDO ELEMENTOS QUE NO VINIERON
            all_odoo_recordsets.filtered(lambda x: x.codRegimen not in all_external_ley_list).write({
                'active': False
            })

    def _prepare_values(self, external_record):
        return {
            'descripcionRegimen': external_record.descripcionRegimen,
            'indVencimiento': external_record.indVencimiento == 'S',
            'presupuesto': external_record.presupuesto == 'S',
            'vigente': external_record.vigente == 'S',
            'active': True
        }
