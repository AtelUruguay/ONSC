# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDesempenoSettings(models.Model):
    _name = 'onsc.desempeno.settings'
    _description = u"Configuración"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    descriptor1_ids = fields.One2many('onsc.catalog.descriptor1', related="company_id.descriptor1_ids",
                                      string="Escalafones excluidos", readonly=False, related_sudo=True)

    def execute(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def write(self, vals):
        res = super(ONSCDesempenoSettings, self.suspend_security()).write(vals)
        return res


class ONSCCatalogDescriptor1(models.Model):
    _name = 'onsc.catalog.descriptor1'
    _description = u'Descriptor 1'
    _inherit = ['onsc.catalog.descriptor1']

    company_id = fields.Many2one("res.company", string="Mapeo Configuración Desempeño ",
                                            ondelete='restrict', )
