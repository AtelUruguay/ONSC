# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluationStage(models.Model):
    _name = 'onsc.desempeno.evaluation.stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Etapa de evaluaciones 360° por UE'

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
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string=u'Año a evaluar',
                                       domain=[("active", "=", True)],
                                       required=True, tracking=True)
    year = fields.Integer(
        u'Año a evaluar',
        related="general_cycle_id.year",
        store=True)
    inciso_id = fields.Many2one(
        "onsc.catalog.inciso",
        string="Inciso",
        related="operating_unit_id.inciso_id",
        store=True)
    start_date = fields.Date(string=u'Fecha inicio', required=True, tracking=True)
    end_date_environment = fields.Date(string=u'Fecha fin def. entorno', required=True, tracking=True)
    end_date = fields.Date(string=u'Fecha fin', required=True, tracking=True)
    active = fields.Boolean(string="Activo", default=True, tracking=True)
    closed_stage = fields.Boolean(string="Etapa cerrada", default=False, tracking=True)
    show_buttons = fields.Boolean(string="Editar datos de contrato", compute='_compute_show_buttons')
    is_edit_start_date = fields.Boolean(string="Editar datos de destino", compute='_compute_is_edit_start_date')
    is_edit_end_date_environment = fields.Boolean(string="Editar datos de origen",
                                                  compute='_compute_is_edit_end_date_environment')
    is_edit_end_date = fields.Boolean(string="Editar datos de origen", compute='_compute_is_edit_end_date')
    name = fields.Char('Nombre', compute='_compute_name')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    @api.depends('start_date')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.start_date and record.start_date < fields.Date.today()

    @api.depends('end_date')
    def _compute_show_buttons(self):
        for record in self:
            record.show_buttons = record.end_date and record.end_date <= fields.Date.today()

    @api.depends('start_date')
    def _compute_is_edit_start_date(self):
        for record in self:
            record.is_edit_start_date = not record.id or record.start_date < fields.Date.today()

    @api.depends('end_date_environment')
    def _compute_is_edit_end_date_environment(self):
        for record in self:
            record.is_edit_end_date_environment = not record.id or record.end_date_environment < fields.Date.today()

    @api.depends('end_date')
    def _compute_is_edit_end_date(self):
        for record in self:
            record.is_edit_end_date = not record.id or record.end_date < fields.Date.today()

    @api.depends('operating_unit_id', 'general_cycle_id')
    def _compute_name(self):
        for record in self:
            record.name = "%s - %s" % (record.operating_unit_id.name or '', record.general_cycle_id.year)

    @api.constrains('general_cycle_id', 'operating_unit_id')
    def _check_unique_config(self):
        EvalutionStage = self.env['onsc.desempeno.evaluation.stage'].suspend_security()
        for record in self:
            evaluations_qty = EvalutionStage.search_count(
                [("general_cycle_id", "=", record.general_cycle_id.id),
                 ("operating_unit_id", "=", record.operating_unit_id.id), ("id", "!=", record.id)])
            if evaluations_qty > 0:
                raise ValidationError(_(u"Solo se puede tener una configuración para el año"))

    @api.constrains('start_date')
    def _check_start_date_today(self):
        for record in self:
            if record.start_date < fields.Date.today():
                raise ValidationError(_("La fecha inicio debe ser menor o igual a la fecha actual"))

    @api.constrains('end_date')
    def _check_end_date_today(self):
        for record in self:
            if record.end_date < fields.Date.today():
                raise ValidationError(_("La fecha fin debe ser mayor o igual a la fecha actual"))

    @api.constrains("start_date", "general_cycle_id.start_date", "general_cycle_id.start_date_max")
    def _check_start_dates(self):
        for record in self:
            if record.start_date < record.general_cycle_id.start_date:
                raise ValidationError(
                    _(u"La fecha inicio de las Etapas de evaluaciones 360° por UE de debe ser mayor o igual a la fecha de inicio del Ciclo General"))
            if record.start_date < record.general_cycle_id.start_date_max:
                raise ValidationError(
                    _(u"La fecha inicio de las Etapas de evaluaciones 360° por UE de debe ser mayor o igual a la fecha de inicio máxima del Ciclo General"))

    @api.constrains("end_date", "general_cycle_id.end_date_max")
    def _check_end_dates(self):
        for record in self:
            if record.end_date > record.general_cycle_id.end_date_max:
                raise ValidationError(
                    _(u"La fecha de fin de las Etapas de evaluaciones 360° por UE de debe ser menor o igual a la fecha de fin máxima del Ciclo General"))

    @api.constrains("start_date", "end_date", "end_date_environment")
    def _check_dates(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError(_(u"La fecha inicio debe ser menor o igual a la fecha de fin"))
            if record.end_date_environment > record.end_date:
                raise ValidationError(
                    _(u"La Fecha fin def. entorno debe ser menor o igual a la fecha de fin"))
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
    def onchange_general_cycle_id(self):
        if self.general_cycle_id:
            self.start_date = self.general_cycle_id.start_date_max
            self.end_date = self.general_cycle_id.end_date_max

    def toggle_active(self):
        self._check_toggle_active()
        return super(ONSCDesempenoEvaluationStage, self.with_context(no_check_write=True)).toggle_active()

    def action_extend_deadline(self):
        return True

    def action_close_stage(self):
        self.write({'closed_stage': True})
        return True

    def _check_toggle_active(self):
        if not self.active:
            if self.env['onsc.desempeno.general.cycle'].suspend_security().search_count(
                    [('id', '=', self.general_cycle_id.id)]) == 0:
                raise ValidationError(
                    _("No se pueden desarchivar Etapa de evaluaciones 360° si no esta activa la configuración"))
            self._check_unique_config()
            self._check_date()
        return True
