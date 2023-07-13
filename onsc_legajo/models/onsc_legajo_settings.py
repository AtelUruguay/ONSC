# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVSettings(models.TransientModel):
    _name = 'onsc.legajo.settings'
    _description = u"Configuración"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    ascenso_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        related="company_id.ascenso_causes_discharge_id",
        string="Causal de egreso por Ascenso",
        readonly=False,
        related_sudo=True
    )
    transforma_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        related="company_id.transforma_causes_discharge_id",
        string="Causal de egreso por Transformación",
        readonly=False,
        related_sudo=True
    )
    reestructura_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        related="company_id.reestructura_causes_discharge_id",
        string="Causal de egreso por Reestructura",
        readonly=False,
        related_sudo=True
    )

    def execute(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def write(self, vals):
        res = super(ONSCCVSettings, self.suspend_security()).write(vals)
        return res
