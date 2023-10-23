# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCDesempenoSettings(models.Model):
    _name = 'onsc.desempeno.settings'
    _description = u"Configuración"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    descriptor1_ids = fields.Many2many('onsc.catalog.descriptor1', related="company_id.descriptor1_ids",
                                       groups='onsc_desempeno.group_desempeno_configurador_escalafones',
                                       string="Escalafones excluidos", readonly=False, related_sudo=True)
    is_evaluation_form_active = fields.Boolean(related="company_id.is_evaluation_form_active", readonly=False,
                                               related_sudo=True)
    evaluation_form_text = fields.Text(related="company_id.evaluation_form_text", readonly=False, related_sudo=True)
    is_environment_evaluation_form_active = fields.Boolean(related="company_id.is_environment_evaluation_form_active",
                                                           readonly=False, related_sudo=True)
    environment_evaluation_text = fields.Text(related="company_id.environment_evaluation_text", readonly=False,
                                              related_sudo=True)
    max_desempenno_evaluation_forms = fields.Integer(string='Tope de formularios de desempeño',)

    def execute(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def write(self, vals):
        res = super(ONSCDesempenoSettings, self.suspend_security()).write(vals)
        return res
