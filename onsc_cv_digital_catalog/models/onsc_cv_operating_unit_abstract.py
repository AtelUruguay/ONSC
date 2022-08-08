# -*- coding: utf-8 -*-

import json

from odoo import fields, models, api


def calc_company_name(record):
    if record.inciso_id and record.operating_unit_id and not record.company_name:
        return '%s-%s' % (record.inciso_id.display_name, record.operating_unit_id.display_name)
    elif record.inciso_id and record.operating_unit_id and record.company_name:
        return '%s-%s-%s' % (record.inciso_id.display_name, record.operating_unit_id.display_name, record.company_name)
    else:
        return record.company_name


class ONSCCVOperatingUnitAbstract(models.AbstractModel):
    _name = 'onsc.cv.operating.unit.abstract'
    _description = 'Clase abstracta de unidad ejecutora e inciso'

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
                domain += ['|', ('start_date', '=', False), ('start_date', '<=', fields.Date.to_string(rec.start_date))]
            if rec.end_date:
                domain += ['|', ('end_date', '>=', fields.Date.to_string(rec.end_date)), ('end_date', '=', False)]
            self.inciso_id_domain = json.dumps(domain)

    @api.depends('start_date', 'end_date', 'inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            if rec.inciso_id.id is False:
                self.operating_unit_id_domain = json.dumps([('id', 'in', [])])
            else:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
                if rec.start_date:
                    domain = ['&'] + domain + [('start_date', '<=', fields.Date.to_string(rec.start_date))]
                if rec.end_date:
                    domain = ['&'] + domain + ['|', ('end_date', '>=', fields.Date.to_string(rec.end_date)),
                                               ('end_date', '=', False)]
                self.operating_unit_id_domain = json.dumps(domain)

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        if self.inciso_id.id is False or (
                self.inciso_id and self.operating_unit_id and self.operating_unit_id.inciso_report_id != self.inciso_id):
            self.operating_unit_id = False

    @api.onchange('start_date')
    def onchange_start_date_check_inciso(self):
        self.inciso_id = False
        self.operating_unit_id = False

    @api.onchange('end_date')
    def onchange_end_date_check_inciso(self):
        self.inciso_id = False
        self.operating_unit_id = False
