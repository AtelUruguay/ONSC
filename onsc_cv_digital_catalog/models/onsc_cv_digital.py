# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalWorkExperience(models.Model):
    _inherit = 'onsc.cv.work.experience'

    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso")
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        domain=[('inciso_id', '=', inciso_id)])


class ONSCCVDigitalVolunteering(models.Model):
    _inherit = 'onsc.cv.volunteering'

    inciso_id = fields.Many2one("onsc.catalog.inciso", string="Inciso")
    operating_unit_id = fields.Many2one("operating.unit",
                                        string="Unidad ejecutora",
                                        domain=[('inciso_id', '=', inciso_id)])
