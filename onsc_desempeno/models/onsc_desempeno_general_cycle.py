# -*- coding: utf-8 -*-
import logging

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoGeneralCycle(models.Model):
    _name = 'onsc.desempeno.general.cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Ciclo general de evaluación de desempeño'
    _rec_name = 'year'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCDesempenoGeneralCycle, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                     toolbar=toolbar,
                                                                     submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_config = self.env.user.has_group('onsc_desempeno.group_desempeno_configurador_gh_ue')
        is_user_admin = self.env.user.has_group('onsc_desempeno.group_desempeno_administrador')
        if view_type in ['form', 'tree', 'kanban'] and is_user_config and not is_user_admin:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(ONSCDesempenoGeneralCycle, self).default_get(fields_list)
        res['year'] = fields.Date.today().strftime('%Y')
        return res

    year = fields.Integer(u'Año a evaluar', required=True, tracking=True)
    start_date = fields.Date(string=u'Fecha inicio', required=True, tracking=True)
    end_date = fields.Date(string=u'Fecha fin', required=True, tracking=True)
    start_date_max = fields.Date(string=u'Fecha inicio máx.', required=True, tracking=True)
    end_date_max = fields.Date(string=u'Fecha fin máx.', required=True, tracking=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True)

    is_edit_start_date = fields.Boolean(
        string="Editar datos de destino",
        compute='_compute_is_edit_start_date')
    is_edit_start_date_max = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_start_date_max')
    is_edit_end_date_max = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_end_date_max')
    is_edit_end_date = fields.Boolean(
        string="Editar datos de origen",
        compute='_compute_is_edit_end_date')

    @api.depends('start_date')
    def _compute_is_edit_start_date(self):
        for record in self:
            record.is_edit_start_date = not record.id or record.start_date > fields.Date.today()

    @api.depends('start_date_max')
    def _compute_is_edit_start_date_max(self):
        for record in self:
            record.is_edit_start_date_max = not record.id or record.start_date_max > fields.Date.today()

    @api.depends('end_date_max')
    def _compute_is_edit_end_date_max(self):
        for record in self:
            record.is_edit_end_date_max = not record.id or record.end_date_max > fields.Date.today()

    @api.depends('end_date')
    def _compute_is_edit_end_date(self):
        for record in self:
            record.is_edit_end_date = not record.id or record.end_date > fields.Date.today()

    @api.constrains('start_date')
    def _check_start_date(self):
        for record in self:
            if record.start_date < fields.Date.today():
                raise ValidationError(_("La fecha inicio debe ser mayor o igual a la fecha actual"))

    @api.constrains('end_date')
    def _check_end_date_today(self):
        for record in self:
            if record.end_date < fields.Date.today():
                raise ValidationError(_("La fecha fin debe ser mayor o igual a la fecha actual"))

    @api.constrains("start_date", "end_date", "start_date_max", "end_date_max", "year")
    def _check_date(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.start_date_max > record.end_date_max:
                raise ValidationError(_(u"La fecha inicio máxima debe ser menor o igual a la fecha de fin máxima"))
            if record.start_date_max < record.start_date:
                raise ValidationError(_(u"La fecha inicio máxima debe ser mayor o igual a la fecha de inicio"))
            if record.end_date_max > record.end_date:
                raise ValidationError(_(u"La fecha fin máxima debe ser menor o igual a la fecha de fin"))

            if int(record.start_date.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha inicio debe estar dentro del año %s") % record.year)
            if int(record.end_date_max.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha fin máxima debe estar dentro del año %s") % record.year)
            if int(record.start_date_max.strftime('%Y')) != record.year:
                raise ValidationError(
                    _("La fecha inicio máxima debe estar dentro del año %s") % record.year)

            # evaluations_qty = self.env['onsc.desempeno.evaluation.stage'].suspend_security().search_count(
            #     ['&', ("general_cycle_id", "=", record.id), '|', '|', ("start_date", ">", record.start_date_max),
            #      ("start_date", "<", record.start_date), ("end_date", ">", record.end_date_max)])
            # if evaluations_qty > 0:
            #     raise ValidationError(
            #         _(u"No se cumple las condiciones de la etapa de evaluaciones 360° por UE "
            #           u"que esta asociada a ciclo general de evaluación de desempeño"))

    @api.constrains('year')
    def _check_unique_config(self):
        GeneralCycle = self.env['onsc.desempeno.general.cycle'].suspend_security()
        for record in self:
            general_qty = GeneralCycle.search_count(
                [("year", "=", record.year), ("id", "!=", record.id)])
            if general_qty > 0:
                raise ValidationError(_(u"Solo se puede tener una configuración para el año"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        year = self.search([], limit=1, order="year desc").year + 1

        default['year'] = _("%s") % year
        default['start_date'] = _("%s") % '%s-' % year + self.start_date.strftime('%m-%d')
        default['end_date'] = _("%s") % '%s-' % year + self.end_date.strftime('%m-%d')
        default['start_date_max'] = _("%s") % '%s-' % year + self.start_date_max.strftime('%m-%d')
        default['end_date_max'] = _("%s") % '%s-' % year + self.end_date_max.strftime('%m-%d')

        return super(ONSCDesempenoGeneralCycle, self).copy(default=default)

    def disable_evaluation(self):
        self.search([('end_date', '<', fields.Date.today())]).write({'active': False})
        self.env['onsc.desempeno.evaluation.stage'].suspend_security().search(
            [('end_date', '<', fields.Date.today())]).write({'active': False, 'closed_stage': True})

    def toggle_active(self):
        self._check_toggle_active()
        return super(ONSCDesempenoGeneralCycle, self.with_context(no_check_write=True)).toggle_active()

    def _check_toggle_active(self):
        if not self.env.user.has_group('onsc_desempeno.group_desempeno_administrador'):
            raise ValidationError(
                _("No tiene permiso para archivar o desarchivar"))

        if not self.active:
            self._check_unique_config()
        return True

    def unlink(self):
        self._check_can_unlink()
        return super(ONSCDesempenoGeneralCycle, self).unlink()

    def _check_can_unlink(self):
        if self.env['onsc.desempeno.evaluation.stage'].suspend_security().search_count(
                [('general_cycle_id', 'in', self.ids)]) > 0:
            raise ValidationError(
                _("No se pueden eliminar configuraciones mientas se tenga una Etapa de evaluaciones 360° activa"))
