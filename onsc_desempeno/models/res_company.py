# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    descriptor1_ids = fields.Many2many('onsc.catalog.descriptor1',
                                      string='Escalafones excluidos', ondelete='restrict')

    def write(self, vals):
        if len(vals) == 1 and 'descriptor1_ids' in vals:
            return super(ResCompany, self.suspend_security()).write(vals)
        return super(ResCompany, self).write(vals)
