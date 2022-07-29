# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.experience'

    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso")
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        domain=[('inciso_id', '=', inciso_id)])
    company_name_clac = fields.Char('Empresa', compute='_compute_company_name_clac')

    @api.depends('inciso_id', 'operating_unit_id', 'company_name')
    def _compute_company_name_clac(self):
        for rec in self:
            if rec.inciso_id and rec.operating_unit_id and rec.company_name:
                rec.company_name_clac = '%s-%s-%s' % (
                    rec.inciso_id.short_name, rec.operating_unit_id.budget_code, rec.company_name)
            else:
                rec.company_name_clac = rec.company_name


class ONSCCVDigitalVolunteering(models.Model):
    _inherit = 'onsc.cv.volunteering'

    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso")
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        domain=[('inciso_id', '=', inciso_id)])
    company_name_clac = fields.Char('Empresa', compute='_compute_company_name_clac')

    @api.depends('inciso_id', 'operating_unit_id', 'company_name')
    def _compute_company_name_clac(self):
        for rec in self:
            if rec.inciso_id and rec.operating_unit_id and rec.company_name:
                rec.company_name_clac = '%s-%s-%s' % (
                    rec.inciso_id.short_name, rec.operating_unit_id.budget_code, rec.company_name)
            else:
                rec.company_name_clac = rec.company_name
