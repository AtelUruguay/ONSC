# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api, tools, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCLegajoOffice(models.Model):
    _name = 'onsc.legajo.office'
    _inherit = ['onsc.legajo.abstract.sync']
    _description = 'Oficina'
    _rec_name = 'code'

    code = fields.Char(string="Código", compute='_compute_code', store=True, index=True)
    inciso = fields.Many2one("onsc.catalog.inciso", string="Inciso", required=True)
    inciso_budget_code = fields.Char(u"Inciso - Código presupuestal (SIIF)", related='inciso.budget_code', store=True)
    unidadEjecutora = fields.Many2one("operating.unit", string="Unidad ejecutora", required=True)
    unidadEjecutora_budget_code = fields.Char(u"Unidad ejecutora - Código presupuestal (SIIF)",
                                              related='unidadEjecutora.budget_code', store=True)
    programa = fields.Char(string="Código del programa")
    programaDescripcion = fields.Char(string="Descripción del programa")
    proyecto = fields.Char(string="Código del proyecto")
    proyectoDescripcion = fields.Char(string="Descripción del proyecto")

    jornada_retributiva_ids = fields.One2many("onsc.legajo.jornada.retributiva",
                                              inverse_name="office_id",
                                              string="Jornadas retributivas")

    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'El código de la oficina debe ser único')
    ]

    def name_get(self):
        res = []
        for record in self:
            name = record.code
            if self._context.get('show_project_program', False) and (record.programa or record.programaDescripcion):
                name = 'Programa %s - %s / Proyecto %s - %s' % (
                    record.programa,
                    record.programaDescripcion,
                    record.proyecto,
                    record.proyectoDescripcion,
                )
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        by_name = super(ONSCLegajoOffice, self).name_search(name, args=args, operator=operator, limit=limit)
        if self._context.get('show_project_program', False):
            by_domain = ['|', '|', '|',
                         ('programa', operator, name),
                         ('programaDescripcion', operator, name),
                         ('proyecto', operator, name),
                         ('proyectoDescripcion', operator, name)
                         ] + args
            by_search = self.search(by_domain, limit=limit)
            return list(set(by_name + by_search.name_get()))
        return by_name

    def _custom_display_name(self):
        return 'Programa %s - %s / Proyecto %s - %s' % (
            self.programa,
            self.programaDescripcion,
            self.proyecto,
            self.proyectoDescripcion,
        )

    @api.depends('inciso', 'unidadEjecutora', 'programa', 'proyecto')
    def _compute_code(self):
        for record in self:
            _code = _('Inciso: %s - UE: %s') % (
                record.suspend_security().inciso.budget_code, record.suspend_security().unidadEjecutora.budget_code)
            if record.programa:
                _code += _(' - Programa: %s') % (record.programa)
            if record.proyecto:
                _code += _(' - Proyecto: %s') % (record.proyecto)
            record.code = _code

    @api.onchange('inciso')
    def onchange_inciso(self):
        self.unidadEjecutora = False

    @api.model
    def syncronize(self, log_info=False):
        parameter = self.env['ir.config_parameter'].sudo().get_param('onsc_legajo_WS13_oficinas')
        cron = self.env.ref("onsc_legajo.sync_legajo_office")
        integration_error = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS13_9005")
        wsclient = self._get_client(parameter, cron.name, integration_error)
        return self.with_context(log_info=log_info).suspend_security()._syncronize(wsclient, parameter, cron.name,
                                                                                   integration_error, {})

    def _populate_from_syncronization(self, response):
        # pylint: disable=invalid-commit
        JornadaRetributiva = self.env['onsc.legajo.jornada.retributiva']
        all_odoo_recordsets = JornadaRetributiva.search([('active', 'in', [False, True])])
        all_odoo_recordsets_key_list = all_odoo_recordsets.mapped('code')

        all_external_ley_list = []
        cron = self.env.ref("onsc_legajo.sync_legajo_office")
        integration_error_WS13_9000 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS13_9000")
        integration_error_WS13_9001 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS13_9001")
        integration_error_WS13_9002 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS13_9002")

        offices = self._get_offices(response.listaOficinasJornada, cron)

        with self._cr.savepoint():
            for external_record in response.listaOficinasJornada:
                key_str = JornadaRetributiva._get_code_by_keyparams(
                    external_record.inciso,
                    external_record.unidadEjecutora,
                    external_record.codigoJornada,
                    external_record.programa,
                    external_record.proyecto)
                all_external_ley_list.append(key_str)

                vals = self._prepare_values(external_record, offices, cron)
                # CREANDO NUEVO ELEMENTO
                if key_str not in all_odoo_recordsets_key_list:
                    try:
                        JornadaRetributiva.create(vals)
                        if self._context.get('log_info'):
                            self.create_new_log(
                                origin=cron.name,
                                type='info',
                                integration_log=integration_error_WS13_9000,
                                ws_tuple=external_record,
                                long_description='Evento: Creación'
                            )
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin=cron.name,
                            type='error',
                            integration_log=integration_error_WS13_9001,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
                # MODIFICANDO ELEMENTO EXISTENTE
                else:
                    try:
                        all_odoo_recordsets.filtered(lambda x: x.code == key_str).write(vals)
                        if self._context.get('log_info'):
                            self.create_new_log(
                                origin=cron.name,
                                type='info',
                                integration_log=integration_error_WS13_9000,
                                ws_tuple=external_record,
                                long_description='Evento: Actualización'
                            )
                    except Exception as e:
                        _logger.warning(tools.ustr(e))
                        self.create_new_log(
                            origin=cron.name,
                            type='error',
                            integration_log=integration_error_WS13_9002,
                            ws_tuple=external_record,
                            long_description=tools.ustr(e))
            # DESACTIVANDO ELEMENTOS QUE NO VINIERON
            all_odoo_recordsets.filtered(lambda x: x.code not in all_external_ley_list).write({
                'active': False
            })

    def _get_offices(self, listaOficinasJornada, cron):
        Inciso = self.env['onsc.catalog.inciso']
        OperatingUnit = self.env['operating.unit']
        all_offices = self.env['onsc.legajo.office'].search([('active', 'in', [False, True])])
        all_odoo_recordsets_codes = all_offices.mapped('code')
        all_offices_codes2active = []
        all_external_ley_list = []
        with self._cr.savepoint():
            for external_record in listaOficinasJornada:
                try:
                    new_office_code = self._get_code_by_keyparams(
                        external_record.inciso,
                        external_record.unidadEjecutora,
                        external_record.programa,
                        external_record.proyecto)
                    inciso = Inciso.suspend_security().search([
                        ('budget_code', '=', str(external_record.inciso))], limit=1)
                    operating_unit = OperatingUnit.suspend_security().search([
                        ('inciso_id', '=', inciso.id),
                        ('budget_code', '=', str(external_record.unidadEjecutora))], limit=1)
                    if inciso.id and operating_unit.id:
                        all_external_ley_list.append(new_office_code)
                    if new_office_code not in all_odoo_recordsets_codes:
                        if inciso.id is False:
                            raise ValidationError(
                                _('El inciso con código %s no ha sido identificado') % str(external_record.inciso))
                        if operating_unit.id is False:
                            raise ValidationError(
                                _('La unidad ejecutora con código %s para el inciso %s no ha sido identificada') %
                                (str(external_record.unidadEjecutora), str(external_record.inciso)))
                        new_office = self.create({
                            'inciso': inciso.id,
                            'unidadEjecutora': operating_unit.id,
                            'programa': str(external_record.programa) or False,
                            'programaDescripcion': external_record.programaDescripcion,
                            'proyecto': str(external_record.proyecto) or False,
                            'proyectoDescripcion': external_record.proyectoDescripcion,
                        })
                        all_offices |= new_office
                        all_odoo_recordsets_codes.append(new_office.code)
                    elif inciso.id and operating_unit.id:
                        all_offices_codes2active.append(new_office_code)
                except Exception as e:
                    _logger.warning(tools.ustr(e))
                    onsc_legajo_integration_error_WS13_9004 = self.env.ref(
                        "onsc_legajo.onsc_legajo_integration_error_WS13_9004")
                    self.create_new_log(
                        origin=cron.name,
                        type='error',
                        integration_log=onsc_legajo_integration_error_WS13_9004,
                        ws_tuple=external_record,
                        long_description=tools.ustr(e))
            # DESACTIVANDO ELEMENTOS QUE NO VINIERON
            all_offices.filtered(lambda x: x.code not in all_external_ley_list).write({
                'active': False
            })
            all_offices.filtered(lambda x: x.active is False and x.code in all_offices_codes2active).write({
                'active': True
            })
        return all_offices

    def _prepare_values(self, external_record, offices, cron):
        try:
            with self._cr.savepoint():
                office_code = self._get_code_by_keyparams(external_record.inciso,
                                                          external_record.unidadEjecutora,
                                                          external_record.programa,
                                                          external_record.proyecto)
                office = offices.filtered(lambda x: x.code == office_code)

                if office.id is False:
                    raise ValidationError(
                        _("Al crear la jornada retributiva %s no se ha podido identificar la oficina %s") % (
                            str(external_record.codigoJornada), office_code))

                vals = {
                    'office_id': office.id,
                    'codigoJornada': str(external_record.codigoJornada),
                    'descripcionJornada': external_record.descripcionJornada,
                    'active': True
                }
                return vals
        except Exception as e:
            _logger.warning(tools.ustr(e))
            integration_error_WS13_9004 = self.env.ref("onsc_legajo.onsc_legajo_integration_error_WS13_9004")
            self.create_new_log(
                origin=cron.name,
                type='error',
                integration_log=integration_error_WS13_9004,
                ws_tuple=external_record,
                long_description=tools.ustr(e))

    def _get_code_by_keyparams(self, inciso, unidadEjecutora, programa=False, proyecto=False):
        code = _('Inciso: %s - UE: %s') % (inciso, unidadEjecutora)
        code += _(' - Programa: %s') % (programa)
        code += _(' - Proyecto: %s') % (proyecto)
        return code

    def _get_office_by_keyparams(self, inciso, unidadEjecutora, programa=False, proyecto=False):
        code = self._get_code_by_keyparams(inciso, unidadEjecutora, programa, proyecto)
        return self.search([('code', '=', code)], limit=1)


class ONSCLegajoJornadaRetributiva(models.Model):
    _name = 'onsc.legajo.jornada.retributiva'
    _description = 'Jornada retributiva'
    _rec_name = 'code'

    office_id = fields.Many2one("onsc.legajo.office", string="Oficina", required=True, ondelete='cascade')
    code = fields.Char(string="Código", compute='_compute_code', store=True, index=True)
    codigoJornada = fields.Char(string="Código de la jornada", required=True)
    descripcionJornada = fields.Char(string="Descripción de la Jornada", required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('codigoJornada_uniq', 'unique("codigoJornada","office_id")',
         u'El código de la jornada retributiva debe ser único por oficina')
    ]

    @api.depends('office_id.code', 'codigoJornada')
    def _compute_code(self):
        for record in self:
            record.code = _('%s - Jornada ret: %s') % (record.office_id.code, record.codigoJornada)

    def _get_code_by_keyparams(self, inciso, unidadEjecutora, codigoJornada, programa=False, proyecto=False):
        office_code = self.env['onsc.legajo.office']._get_code_by_keyparams(inciso, unidadEjecutora, programa, proyecto)
        return _('%s - Jornada ret: %s') % (office_code, codigoJornada)

    def name_get(self):
        res = []
        for record in self:
            name = record.code
            if self._context.get('show_only_description', False):
                name = record.descripcionJornada
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        by_name = super(ONSCLegajoJornadaRetributiva, self).name_search(name, args=args, operator=operator, limit=limit)
        if self._context.get('show_only_description', False):
            by_descripcionJornada_domain = [('descripcionJornada', operator, name)]
            by_descripcionJornada_domain += args
            by_descripcionJornada = self.search(by_descripcionJornada_domain, limit=limit)
            return list(set(by_name + by_descripcionJornada.name_get()))
        return by_name

    def _custom_display_name(self):
        return self.descripcionJornada
