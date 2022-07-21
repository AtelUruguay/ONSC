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
    address_info_date = fields.Date(string="Fecha de información domicilio",
                                    related='partner_id.address_info_date',
                                    readonly=False,
                                    store=True)
    disability_date = fields.Date(string="Fecha de información discapacidad")

    @api.depends('is_cv_gender_public')
    def _compute_gender_public_visualization_date(self):
        for record in self:
            record.gender_public_visualization_date = fields.Date.today()

    @api.onchange('is_docket')
    def onchange_is_docket(self):
        if self.is_docket is False:
            self.gender_date = False
            self.afro_descendant_date = False
            self.status_civil_date = False
            self.address_info_date = False
            self.disability_date = False
