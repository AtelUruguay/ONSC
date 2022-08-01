# -*- coding: utf-8 -*-

from odoo import fields, models, api


def calc_company_name(record):
    if record.inciso_id and record.operating_unit_id and record.company_name:
        return '%s-%s-%s' % (
            record.inciso_id.short_name, record.operating_unit_id.budget_code, record.company_name)
    else:
        return record.company_name


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.experience'

    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso")
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        domain=[('inciso_id', '=', inciso_id)])
    company_name_calc = fields.Char('Empresa', compute='_compute_company_name_calc')

    @api.depends('inciso_id', 'operating_unit_id', 'company_name')
    def _compute_company_name_calc(self):
        for rec in self:
            rec.company_name_calc = calc_company_name(rec)


class ONSCCVDigitalVolunteering(models.Model):
    _inherit = 'onsc.cv.volunteering'

    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso")
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        domain=[('inciso_id', '=', inciso_id)])
    company_name_calc = fields.Char('Empresa', compute='_compute_company_name_calc')

    @api.depends('inciso_id', 'operating_unit_id', 'company_name')
    def _compute_company_name_calc(self):
        for rec in self:
            rec.company_name_calc = calc_company_name(rec)
