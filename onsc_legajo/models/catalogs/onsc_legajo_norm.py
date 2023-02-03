# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools, _

from ...soap import soap_client

_logger = logging.getLogger(__name__)


class ONSCLegajoNorm(models.Model):
    _name = 'onsc.legajo.norm'
    _description = 'Norma'
    _rec_name = 'pk'

    pk = fields.Char(string=u"Código de la norma", required=True)
    anioNorma = fields.Integer(string=u"Año")
    numeroNorma = fields.Integer(string=u"Número")
    articuloNorma = fields.Integer(string=u"Artículo")
    numeroLiteral = fields.Char(string="Número literal")
    tipoNormaSigla = fields.Char(string="Tipo norma sigla")
    tipoNorma = fields.Char(string="Tipo norma")
    descripcion = fields.Char(string=u"Descripción")
    fechaDerogacion = fields.Date(string=u"Fecha derogación")
    fechaVencimiento = fields.Date(string="Fecha vencimiento")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('pk_uniq', 'unique(pk)', u'El código de la norma debe ser único')
    ]

    @api.model
    def syncronize(self):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS3_normas')
        cron = self.env.ref("onsc_legajo.sync_legajo_norm")
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")
        return self._syncronize(parameter, cron.name, integration_error)

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        all_odoo_recordsets = self.search([('active', 'in', [False, True])])
        all_odoo_recordsets_key_list = all_odoo_recordsets.mapped('pk')

        all_external_ley_list = []
        cron = self.env.ref("onsc_legajo.sync_legajo_norm")
        integration_error_WS3_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9000")
        integration_error_WS3_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9001")
        integration_error_WS3_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9002")

        for external_record in response.listaRegimenPlaza:
            key_str = str(external_record.pk)
            all_external_ley_list.append(key_str)

            vals = self._prepare_values(external_record)
            # CREANDO NUEVO ELEMENTO
            if key_str not in all_odoo_recordsets_key_list:
                try:
                    vals['pk'] = key_str
                    self.create(vals)
                    self._create_log(
                        origin=cron.name,
                        type='info',
                        integration_log=integration_error_WS3_9000,
                        ws_tuple=external_record,
                        long_description='Evento: Creación'
                    )
                except Exception as e:
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self._create_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS3_9001,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
            # MODIFICANDO ELEMENTO EXISTENTE
            else:
                try:
                    all_odoo_recordsets.filtered(lambda x: x.pk == key_str).write(vals)
                    self._create_log(
                        origin=cron.name,
                        type='info',
                        integration_log=integration_error_WS3_9000,
                        ws_tuple=external_record,
                        long_description='Evento: Actualización'
                    )
                except Exception as e:
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self._create_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS3_9002,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
        # DESACTIVANDO ELEMENTOS QUE NO VINIERON
        all_odoo_recordsets.filtered(lambda x: x.pk not in all_external_ley_list).write({
            'active': False
        })

    def _prepare_values(self, external_record):
        return {
            'anioNorma': external_record.anioNorma,
            'numeroNorma': external_record.numeroNorma,
            'articuloNorma': external_record.articuloNorma,
            'numeroLiteral': external_record.numeroLiteral,
            'tipoNormaSigla': external_record.tipoNormaSigla,
            'tipoNorma': external_record.tipoNorma,
            'descripcion': external_record.descripcion,
            'fechaDerogacion': external_record.fechaDerogacion,
            'fechaVencimiento': external_record.fechaVencimiento,
            'active': True
        }
