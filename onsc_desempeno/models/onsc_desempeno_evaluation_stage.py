# -*- coding: utf-8 -*-
import logging

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluationStage(models.Model):
    _name = 'onsc.desempeno.evaluation.stage'
    _description = u'Etapa de evaluaciones 360° por UE'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCDesempenoEvaluationStage, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                        toolbar=toolbar,
                                                                        submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type in ['form', 'tree', 'kanban']:
            for node_form in doc.xpath("//%s" % view_type):
                node_form.set('copy', '0')

        res['arch'] = etree.tostring(doc)

        return res

    def _get_domain(self, args):
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        args = expression.AND([[('operating_unit_id', '=', operating_unit_id.id), ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCDesempenoEvaluationStage, self)._search(args, offset=offset, limit=limit, order=order,
                                                                 count=count,
                                                                 access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def default_get(self, fields):
        res = super(ONSCDesempenoEvaluationStage, self).default_get(fields)
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        res['operating_unit_id'] = operating_unit_id.id

        return res

    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", required=True)
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string=u'Año a evalua',
                                       domain=[("active", "=", True)],
                                       required=True)
    start_date = fields.Date(string=u'Fecha inicio', required=True)
    end_date_environment = fields.Date(string=u'Fecha fin def. entorno', required=True)
    end_date = fields.Date(string=u'Fecha fin', required=True)
    active = fields.Boolean(string="Activo", default=True)
    closed_stage = fields.Boolean(string="Etapa cerrada", default=False)
    show_buttons = fields.Boolean(string="Editar datos de contrato", compute='_compute_show_buttons')
    is_edit_start_date = fields.Boolean(string="Editar datos de destino", compute='_compute_is_edit_start_date')
    is_edit_end_date_environment = fields.Boolean(string="Editar datos de origen",
                                                  compute='_compute_is_edit_end_date_environment')
    is_edit_end_date = fields.Boolean(string="Editar datos de origen", compute='_compute_is_edit_end_date')
    name = fields.Char('Nombre', compute='_compute_name')

    @api.depends('end_date')
    def _compute_show_buttons(self):
        for record in self:
            record.show_buttons = record.end_date and record.end_date <= fields.Date.today()

    @api.depends('start_date')
    def _compute_is_edit_start_date(self):
        for record in self:
            record.is_edit_start_date = not record.id or record.end_date <= fields.Date.today()

    @api.depends('end_date_environment')
    def _compute_is_edit_end_date_environment(self):
        for record in self:
            record.is_edit_end_date_environment = not record.id or record.end_date_environment <= fields.Date.today()

    @api.depends('end_date')
    def _compute_is_edit_end_date(self):
        for record in self:
            record.is_edit_end_date = not record.id or record.end_date <= fields.Date.today()

    @api.depends('operating_unit_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            record.name = "%s - %s" % (record.operating_unit_id.name or '', record.general_cycle_id.year)

    @api.constrains('general_cycle_id', 'operating_unit_id')
    def _check_unique_config(self):
        for record in self:
            evaluations_qty = self.env['onsc.desempeno.evaluation.stage'].suspend_security().search_count(
                [("general_cycle_id", "=", record.general_cycle_id.id),
                 ("operating_unit_id", "=", record.operating_unit_id.id), ("id", "!=", record.id)])
            if evaluations_qty > 0:
                raise ValidationError(_(u"Solo se puede tener una configuración para el año"))

        if record.start_date < fields.Date.today():
            raise ValidationError(_("La fecha inicio debe ser mayor o igual a la fecha actual"))

    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if record.start_date < fields.Date.today():
                raise ValidationError(_("La fecha inicio debe ser mayor o igual a la fecha actual"))

    @api.constrains("start_date", "end_date", "end_date_environment", "general_cycle_id.start_date_max",
                    "general_cycle_id.end_date_max", "general_cycle_id.year")
    def _check_date(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.start_date > record.general_cycle_id.start_date_max:
                raise ValidationError(
                    _(u"La fecha inicio debe ser menor o igual a la fecha de inicio máxima del ciclo general"))
            if record.start_date < record.general_cycle_id.start_date:
                raise ValidationError(
                    _(u"La fecha inicio debe ser mayor o igual a la fecha de inicio del ciclo general"))
            if record.end_date > record.general_cycle_id.end_date_max:
                raise ValidationError(
                    _(u"La fecha fin debe ser menor o igual a la fecha de fin máxima del ciclo general"))
            if record.end_date_environment > record.end_date:
                raise ValidationError(
                    _(u"La Fecha fin def. entorno debe ser menor o igual a la fecha de fin máxima del ciclo general"))
            if int(record.start_date.strftime('%Y')) != record.general_cycle_id.year:
                raise ValidationError(
                    _("La fecha inicio debe estar dentro del año %s") % record.general_cycle_id.year)
            if int(record.end_date.strftime('%Y')) != record.general_cycle_id.year:
                raise ValidationError(
                    _("La fecha fin debe estar dentro del año %s") % record.general_cycle_id.year)
            if int(record.end_date_environment.strftime('%Y')) != record.general_cycle_id.year:
                raise ValidationError(
                    _("La fecha fin def. entorno debe estar dentro del año %s") % record.general_cycle_id.year)

    @api.onchange('general_cycle_id')
    def onchange_end_date(self):
        if self.general_cycle_id:
            self.start_date = self.general_cycle_id.start_date
            self.end_date = self.general_cycle_id.end_date

    def action_extend_deadline(self):
        return True

    def action_close_stage(self):
        return True

