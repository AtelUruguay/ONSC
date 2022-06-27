# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigital(models.Model):
    _inherit = 'onsc.cv.digital'

    # INFORMACION GENERAL---<Page>
    # Información Patronímica
    cv_source_info_auth_type = fields.Selection(related='partner_id.cv_source_info_auth_type')
