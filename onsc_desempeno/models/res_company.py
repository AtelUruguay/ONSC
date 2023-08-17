# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    descriptor1_ids = fields.Many2many('onsc.catalog.descriptor1',
                                       string='Escalafones excluidos', ondelete='restrict')
    is_evaluation_form_active = fields.Boolean('Activar Ayuda para formulario de evaluación')
    evaluation_form_text = fields.Text('Ayuda para formulario de evaluación')
    is_environment_evaluation_form_active = fields.Boolean('Activar ayuda para formulario de definición de entorno')
    environment_evaluation_text = fields.Text('Ayuda para formulario de definición de entorno')

    def write(self, vals):
        _fields = ["is_evaluation_form_active", "evaluation_form_text", "is_environment_evaluation_form_active", "environment_evaluation_text", "descriptor1_ids"]
        if any(x in vals.keys() for x in _fields):
            return super(ResCompany, self.suspend_security()).write(vals)
        return super(ResCompany, self).write(vals)
