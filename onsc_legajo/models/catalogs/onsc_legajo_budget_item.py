# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class ONSCLegajoBudgetItem(models.Model):
    _name = 'onsc.legajo.budget.item'
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
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")
        return self._syncronize(parameter, cron.name, integration_error)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        all_odoo_recordsets = self.search([('active', 'in', [False, True])])
        all_odoo_recordsets_key_list = all_odoo_recordsets.mapped('codPartida')

        all_external_ley_list = []
        cron = self.env.ref("onsc_legajo.sync_legajo_budget_item")
        integration_error_WS2_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9000")
        integration_error_WS2_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9001")
        integration_error_WS2_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS2_9002")

        for external_record in response.listaRegimenPlaza:
            key_str = str(external_record.codPartida)
            all_external_ley_list.append(key_str)

            vals = self._prepare_values(external_record)
            # CREANDO NUEVO ELEMENTO
            if key_str not in all_odoo_recordsets_key_list:
                try:
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
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self._create_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS2_9001,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
            # MODIFICANDO ELEMENTO EXISTENTE
            else:
                try:
                    all_odoo_recordsets.filtered(lambda x: x.codPartida == key_str).write(vals)
                    self._create_log(
                        origin=cron.name,
                        type='info',
                        integration_log=integration_error_WS2_9000,
                        ws_tuple=external_record,
                        long_description='Evento: Actualización'
                    )
                except Exception as e:
                    self.env.cr.commit()
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

    def _prepare_values(self, external_record):
        Descriptor1 = self.env['onsc.catalog.descriptor1']
        Descriptor2 = self.env['onsc.catalog.descriptor2']
        Descriptor3 = self.env['onsc.catalog.descriptor3']
        Descriptor4 = self.env['onsc.catalog.descriptor4']
        vals = {'active': True}
        if external_record.dsc1Id:
            vals['dsc1Id'] = Descriptor1.search([('code', '=', external_record.dsc1Id)], limit=1).id
        if external_record.dsc2Id:
            vals['dsc2Id'] = Descriptor2.search([('code', '=', external_record.dsc2Id)], limit=1).id
        if external_record.dsc3Id:
            descriptor3 = Descriptor3.search([('code', '=', external_record.dsc3Id)], limit=1)
            if descriptor3:
                vals['desc3Id'] = descriptor3.id
            else:
                vals['desc3Id'] = Descriptor3.create({
                    'code': external_record.dsc3Id,
                    'name': external_record.Dsc3Descripcion
                }).id
        if external_record.dsc4Id:
            descriptor4 = Descriptor4.search([('code', '=', external_record.dsc4Id)], limit=1)
            if descriptor4:
                vals['desc4Id'] = descriptor4.id
            else:
                vals['desc4Id'] = Descriptor4.create({
                    'code': external_record.dsc4Id,
                    'name': external_record.Dsc4Descripcion
                }).id
        return vals
