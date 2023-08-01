# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    descriptor1_ids = fields.One2many('onsc.catalog.descriptor1', "desempeno_settings_id",
                                      string='Escalafones excluidos', ondelete='restrict')
