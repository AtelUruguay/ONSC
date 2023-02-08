# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoBudgetItem(models.Model):
    _name = 'onsc.legajo.budget.item'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Partida'

    codPartida = fields.Char(string="Código de partida", required=True)
    dsc1Id = fields.Many2one("onsc.catalog.descriptor1", string="Descriptor 1")
    dsc2Id = fields.Many2one("onsc.catalog.descriptor2", string="Descriptor 2")
    dsc3Id = fields.Many2one("onsc.catalog.descriptor3", string="Descriptor 3", required=True)
    dsc4Id = fields.Many2one("onsc.catalog.descriptor4", string="Descriptor 4")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('code_uniq', 'unique("codPartida")', u'El código de la partida debe ser único'),
    ]

    @api.model
    def syncronize(self):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS2_partidas')
        cron = self.env.ref("onsc_legajo.sync_legajo_budget_item")
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9005")
        return self._syncronize(parameter, cron.name, integration_error, {'dsc1Id': -1, 'dsc2Id': -1, })

    def _populate_from_syncronization(self, response):
        all_odoo_recordsets = self.search([('active', 'in', [False, True])])
        all_odoo_recordsets_key_list = all_odoo_recordsets.mapped('codPartida')

        all_external_ley_list = []
        cron = self.env.ref("onsc_legajo.sync_legajo_budget_item")
        integration_error_WS2_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9000")
        integration_error_WS2_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9001")
        integration_error_WS2_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9002")

        with self._cr.savepoint():
            for external_record in response.listaPartidas:
                key_str = str(external_record.codPartida)
                all_external_ley_list.append(key_str)

                vals = self._prepare_values(external_record, cron)
                # CREANDO NUEVO ELEMENTO
                if vals is not None and key_str not in all_odoo_recordsets_key_list:
                    try:
                        # with self._cr.savepoint():
                        vals['codPartida'] = key_str
                        self.create(vals)
                        self._create_log(
                            origin=cron.name,
                            type='info',
                            integration_log=integration_error_WS2_9000,
                            ws_tuple=external_record,
                            long_description='Evento: Creación'
                        )
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self._create_log(
                            origin=cron.name,
                            type='error',
                            integration_log=integration_error_WS2_9001,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
                # MODIFICANDO ELEMENTO EXISTENTE
                elif vals is not None:
                    try:
                        # with self._cr.savepoint():
                        all_odoo_recordsets.filtered(lambda x: x.codPartida == key_str).write(vals)
                        self._create_log(
                            origin=cron.name,
                            type='info',
                            integration_log=integration_error_WS2_9000,
                            ws_tuple=external_record,
                            long_description='Evento: Actualización'
                        )
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self._create_log(
                            origin=cron.name,
                            type='error',
                            integration_log=integration_error_WS2_9002,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
            # DESACTIVANDO ELEMENTOS QUE NO VINIERON
            all_odoo_recordsets.filtered(lambda x: x.codPartida not in all_external_ley_list).write({
                'active': False
            })

    def _prepare_values(self, external_record, cron):
        try:
            Descriptor1 = self.env['onsc.catalog.descriptor1']
            Descriptor2 = self.env['onsc.catalog.descriptor2']
            Descriptor3 = self.env['onsc.catalog.descriptor3']
            Descriptor4 = self.env['onsc.catalog.descriptor4']
            vals = {
                'dsc1Id': False,
                'dsc2Id': False,
                'dsc3Id': False,
                'dsc4Id': False,
                'active': True
            }
            if external_record.dsc1Id:
                descriptor1 = Descriptor1.suspend_security().search([
                    ('code', '=', str(external_record.dsc1Id))], limit=1)
                if descriptor1.id is False:
                    raise ValidationError(
                        _('El descriptor 1 con código %s no ha sido identificado') % external_record.dsc1Id)
                vals['dsc1Id'] = descriptor1.id
            if external_record.dsc2Id:
                descriptor2 = Descriptor2.suspend_security().search([
                    ('code', '=', str(external_record.dsc2Id))], limit=1)
                if descriptor2.id is False:
                    raise ValidationError(
                        _('El descriptor 2 con código %s no ha sido identificado') % external_record.dsc2Id)
                vals['dsc2Id'] = descriptor2.id
            if external_record.dsc3Id:
                descriptor3 = Descriptor3.suspend_security().search([
                    ('code', '=', str(external_record.dsc3Id))], limit=1)
                if descriptor3.id:
                    vals['dsc3Id'] = descriptor3.id
                else:
                    vals['dsc3Id'] = Descriptor3.suspend_security().create({
                        'code': str(external_record.dsc3Id),
                        'name': external_record.dsc3Descripcion
                    }).id
            if external_record.dsc4Id:
                descriptor4 = Descriptor4.suspend_security().search([
                    ('code', '=', str(external_record.dsc4Id))], limit=1)
                if descriptor4.id:
                    vals['dsc4Id'] = descriptor4.id
                else:
                    vals['dsc4Id'] = Descriptor4.suspend_security().create({
                        'code': str(external_record.dsc4Id),
                        'name': external_record.dsc4Descripcion
                    }).id
            return vals
        except Exception as e:
            _logger.warning(tools.ustr(e))
            integration_error_WS2_9004 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9004")
            self._create_log(
                origin=cron.name,
                type='error',
                integration_log=integration_error_WS2_9004,
                ws_tuple=external_record,
                long_description=tools.ustr(e))
