# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class ONSCLegajoNorm(models.Model):
    _name = 'onsc.legajo.norm'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Norma'
    _rec_name = 'pk'

    pk = fields.Char(string=u"Código de la norma", required=True, index=True)
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
    inciso_ids = fields.Many2many('onsc.catalog.inciso', string="Incisos")

    _sql_constraints = [
        ('pk_uniq', 'unique(pk)', u'El código de la norma debe ser único')
    ]

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS3_normas')
        cron = self.env.ref("onsc_legajo.sync_legajo_norm")
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9005")
        wsclient = self._get_client(parameter, cron.name, integration_error)
        with self._cr.savepoint():
            all_odoo_recordsets = self.search([('active', 'in', [False, True])])
            all_external_key_list = []
            for inciso in self.env['onsc.catalog.inciso'].suspend_security().search([]):
                result = self.with_context(
                    inciso=inciso,
                    log_info=log_info).suspend_security()._syncronize(wsclient,
                                                                      parameter,
                                                                      cron.name,
                                                                      integration_error,
                                                                      inciso.budget_code)
                if isinstance(result, list):
                    all_external_key_list.extend(result)
            all_odoo_recordsets.filtered(lambda x: x.pk not in all_external_key_list).write({
                'active': False
            })
        return True

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        all_external_key_list = []
        if hasattr(response, 'listaClasificador') is False:
            return []
        all_odoo_recordsets = self.search([('active', 'in', [False, True])])
        all_odoo_recordsets_key_list = all_odoo_recordsets.mapped('pk')

        cron = self.env.ref("onsc_legajo.sync_legajo_norm")
        integration_error_WS3_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9000")
        integration_error_WS3_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9001")
        integration_error_WS3_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS3_9002")

        inciso = self._context.get('inciso')
        for external_record in response.listaClasificador:
            key_str = str(external_record.pk)
            all_external_key_list.append(key_str)

            # CREANDO NUEVO ELEMENTO
            if key_str not in all_odoo_recordsets_key_list:
                try:
                    vals = self._prepare_create_values(external_record, inciso)
                    vals['pk'] = external_record.pk
                    self.suspend_security().create(vals)
                    if self._context.get('log_info'):
                        self.create_new_log(
                            origin=cron.name,
                            type='info',
                            integration_log=integration_error_WS3_9000,
                            ws_tuple=external_record,
                            long_description='Evento: Creación'
                        )
                except Exception as e:
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self.create_new_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS3_9001,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
            # MODIFICANDO ELEMENTO EXISTENTE
            else:
                try:
                    recordsets = all_odoo_recordsets.filtered(lambda x: x.pk == key_str)
                    for recordset in recordsets:
                        vals = self._prepare_update_values(external_record, recordset, inciso)
                        recordset.suspend_security().write(vals)
                    if self._context.get('log_info'):
                        self.create_new_log(
                            origin=cron.name,
                            type='info',
                            integration_log=integration_error_WS3_9000,
                            ws_tuple=external_record,
                            long_description='Evento: Actualización'
                        )
                except Exception as e:
                    self.env.cr.commit()
                    _logger.warning(tools.ustr(e))
                    self.create_new_log(
                        origin=cron.name,
                        type='error',
                        integration_log=integration_error_WS3_9002,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
        return all_external_key_list

    def _prepare_create_values(self, external_record, inciso):
        return {
            'anioNorma': external_record.anioNorma,
            'numeroNorma': external_record.numeroNorma,
            'articuloNorma': external_record.articuloNorma,
            'numeroLiteral': external_record.numeroLiteral,
            'tipoNormaSigla': external_record.tipoNormaSigla,
            'tipoNorma': external_record.tipoNorma,
            'descripcion': external_record.descripcion,
            'active': True,
            'inciso_ids': [(6, 0, [inciso.id])]
        }

    def _prepare_update_values(self, external_record, recordset, inciso):
        return {
            'anioNorma': external_record.anioNorma,
            'numeroNorma': external_record.numeroNorma,
            'articuloNorma': external_record.articuloNorma,
            'numeroLiteral': external_record.numeroLiteral,
            'tipoNormaSigla': external_record.tipoNormaSigla,
            'tipoNorma': external_record.tipoNorma,
            'descripcion': external_record.descripcion,
            'active': True,
            'inciso_ids': [(4, inciso.id)]
        }

    def name_get(self):
        res = []
        for record in self:
            name = record.pk
            if self._context.get('show_concatenated_description', False):
                name_parts = []
                name_parts.append(record.tipoNorma + '-' if record.tipoNorma else '')
                name_parts.append(str(record.numeroNorma) + '-' if record.numeroNorma else '0-')
                name_parts.append(str(record.anioNorma) + '-' if record.anioNorma else '0-')
                name_parts.append(str(record.articuloNorma) if record.articuloNorma else '0')
                name = ''.join(name_parts).strip()
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        by_name = super(ONSCLegajoNorm, self).name_search(name, args=args, operator=operator, limit=limit)
        if self._context.get('show_concatenated_description', False):
            by_domain = ['|', '|', '|', ('tipoNorma', operator, name), ('numeroNorma', operator, name),
                         ('anioNorma', operator, name), ('articuloNorma', operator, name)]
            by_domain += args
            by_search = self.search(by_domain, limit=limit)
            return list(set(by_name + by_search.name_get()))
        return by_name

    def _custom_display_name(self):
        name_parts = []
        name_parts.append(self.tipoNorma + '-' if self.tipoNorma else '')
        name_parts.append(str(self.numeroNorma) + '-' if self.numeroNorma else '0-')
        name_parts.append(str(self.anioNorma) + '-' if self.anioNorma else '0-')
        name_parts.append(str(self.articuloNorma) if self.articuloNorma else '0')
        return ''.join(name_parts).strip()
