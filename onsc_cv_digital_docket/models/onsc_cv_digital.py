# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVDigital(models.Model):
    _inherit = 'onsc.cv.digital'

    is_docket = fields.Boolean(string="Tiene legajo")
    gender_date = fields.Date(string="Fecha de información género")
    gender_public_visualization_date = fields.Date(string="Fecha información visualización pública de género",
                                                   compute='_compute_gender_public_visualization_date', store=True)
    afro_descendant_date = fields.Date(string="Fecha de información afrodescendencia")
    status_civil_date = fields.Date(string="Fecha de información estado civil")

    @api.depends('is_cv_gender_public')
    def _compute_gender_public_visualization_date(self):
        for record in self:
            record.gender_public_visualization_date = fields.Date.today()

