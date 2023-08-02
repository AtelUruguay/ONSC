# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    descriptor1_ids = fields.One2many('onsc.catalog.descriptor1', "company_id",
                                      string='Escalafones excluidos', ondelete='restrict')
