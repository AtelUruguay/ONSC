# -*- coding: utf-8 -*-

import json
from odoo import fields, models, api, _
from odoo.addons.onsc_cv_digital.models.onsc_cv_useful_tools import get_onchange_warning_response as cv_warning


def calc_company_name(record):
    if record.inciso_id and record.operating_unit_id and record.company_name:
        return '%s-%s-%s' % (
            record.inciso_id.short_name, record.operating_unit_id.budget_code, record.company_name)
    else:
        return record.company_name


class ONSCCVOperatingUnitAbstract(models.AbstractModel):
    _name = 'onsc.cv.operating.unit.abstract'
    _description = 'Clase abstracta de unidad operativo e inciso'

    inciso_id = fields.Many2one("onsc.catalog.inciso.report", string="Inciso")
    inciso_id_domain = fields.Char(compute='_compute_inciso_id_domain')
    operating_unit_id = fields.Many2one("operating.unit.report",
                                        string="Unidad ejecutora")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    company_name_calc = fields.Char('Empresa', compute='_compute_company_name_calc')

    @api.depends('inciso_id', 'operating_unit_id', 'company_name')
    def _compute_company_name_calc(self):
        for rec in self:
            rec.company_name_calc = calc_company_name(rec)

    @api.depends('start_date', 'end_date')
    def _compute_inciso_id_domain(self):
        for rec in self:
            domain = []
            if rec.start_date:
                domain += ['|', ('date_begin', '=', False), ('date_begin', '<=', fields.Date.to_string(rec.start_date))]
            if rec.end_date:
                domain += ['|', ('date_end', '>=', fields.Date.to_string(rec.end_date)), ('date_end', '=', False)]
            self.inciso_id_domain = json.dumps(domain)

    @api.depends('start_date', 'end_date', 'inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            domain = []
            if rec.inciso_id:
                domain += [('inciso_id', '=', rec.inciso_id.id)]
            if rec.start_date:
                domain += (['|', ('date_begin', '=', False),
                            ('date_begin', '<=', fields.Date.to_string(rec.start_date))])
            if rec.end_date:
                domain += ['|', ('date_end', '>=', fields.Date.to_string(rec.end_date)), ('date_end', '=', False)]
            self.operating_unit_id_domain = json.dumps(domain)

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        if self.inciso_id and self.operating_unit_id and self.operating_unit_id.inciso_report_id != self.inciso_id:
            self.operating_unit_id = False

    @api.onchange('start_date')
    def onchange_start_date_check_inciso(self):
        if self.inciso_id and self.start_date and self.inciso_id.date_begin \
                and self.inciso_id.date_begin > self.start_date:
            self.inciso_id = False
            return cv_warning(_("La fecha de vigencia inicio del inciso debe ser menor o igual que el período desde"))
        if self.inciso_id and self.start_date and self.operating_unit_id.date_begin \
                and self.operating_unit_id.date_begin > self.start_date:
            self.operating_unit_id = False
            return cv_warning(
                _("La fecha de vigencia inicio de la unidad operativa debe ser mayor o igual que el período desde"))

    @api.onchange('end_date')
    def onchange_end_date_check_inciso(self):
        if self.inciso_id and self.end_date and self.inciso_id.date_end and self.inciso_id.date_end < self.end_date:
            self.inciso_id = False
            return cv_warning(_("La fecha de vigencia de fin del inciso debe ser menor o igual el período hasta"))
        if self.inciso_id and self.end_date and self.operating_unit_id.date_end \
                and self.operating_unit_id.date_end < self.end_date:
            self.operating_unit_id = False
            return cv_warning(
                _("La fecha de vigencia de fin de la unidad operativa debe ser mayor o igual el período hasta"))
