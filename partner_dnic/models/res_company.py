# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_dnic_integrated = fields.Boolean('Integración con DNIC')
