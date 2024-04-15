# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    ws7_ascenso_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        string="Causal de egreso por Ascenso",
        ondelete='restrict')
    ws7_transforma_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        string="Causal de egreso por Transformación",
        ondelete='restrict')
    ws7_reestructura_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        string="Causal de egreso por Reestructura",
        ondelete='restrict')
    ws7_date_from = fields.Datetime(
        string='Fecha/hora desde')
    ws7_latency_inseconds = fields.Integer(
        string='Latencia(segundos)')
    mass_upload_record_limit = fields.Integer("Limite Cantidad de Registros")

    def write(self, vals):
        if all('ws7' in key for key in vals.keys()):
            return super(ResCompany, self.suspend_security()).write(vals)
        return super(ResCompany, self).write(vals)
