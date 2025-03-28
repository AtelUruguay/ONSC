# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVSettings(models.TransientModel):
    _name = 'onsc.legajo.settings'
    _description = u"Configuración"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    ws7_ascenso_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        related="company_id.ws7_ascenso_causes_discharge_id",
        string="Causal de egreso por Ascenso",
        readonly=False,
        related_sudo=True
    )
    ws7_transforma_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        related="company_id.ws7_transforma_causes_discharge_id",
        string="Causal de egreso por Transformación",
        readonly=False,
        related_sudo=True
    )
    ws7_reestructura_causes_discharge_id = fields.Many2one(
        "onsc.legajo.causes.discharge",
        related="company_id.ws7_reestructura_causes_discharge_id",
        string="Causal de egreso por Reestructura",
        readonly=False,
        related_sudo=True
    )

    ws7_new_ascenso_reason_description = fields.Char(
        string='Descripción de Alta por Ascenso',
        related="company_id.ws7_new_ascenso_reason_description",
        readonly=False,
        related_sudo=True
    )
    ws7_new_transforma_reason_description = fields.Char(
        string='Descripción de Alta por Transformación',
        related="company_id.ws7_new_transforma_reason_description",
        readonly=False,
        related_sudo=True
    )
    ws7_new_reestructura_reason_description = fields.Char(
        string='Descripción de Alta por Reestructura',
        related="company_id.ws7_new_reestructura_reason_description",
        readonly=False,
        related_sudo=True
    )
    ws7_new_retroactive_reason_description = fields.Char(
        string='Descripción de Alta por Retroactivo',
        related="company_id.ws7_new_retroactive_reason_description",
        readonly=False,
        related_sudo=True
    )
    ws7_date_from = fields.Datetime(
        string='Fecha/hora desde',
        related="company_id.ws7_date_from",
        readonly=False,
        related_sudo=True)
    ws7_latency_inseconds = fields.Integer(
        string='Latencia(segundos)',
        related="company_id.ws7_latency_inseconds",
        readonly=False,
        related_sudo=True)
    mass_upload_record_limit = fields.Integer(
        u"Límite cantidad de registros",
        related="company_id.mass_upload_record_limit",
        readonly=False,
        related_sudo=True)
    ws7_email_list = fields.Char(
        string='Correos electronicos WS7', widget='email',
        related="company_id.ws7_email_list",
        readonly=False,
        related_sudo=True,
        help='Ingresar la lista de correos electronicos separados por coma')
    message_block_summary = fields.Boolean(
        u"Mensaje de sumario bloqueante",
        related="company_id.message_block_summary",
        readonly=False,
        related_sudo=True)
    message_baja_vl_summary = fields.Char(u"Mensaje de baja de vinculo laboral",
                                          related="company_id.message_baja_vl_summary",
                                          readonly=False,
                                          related_sudo=True)
    summary_date_from = fields.Datetime(
        string='Fecha/hora desde',
        related="company_id.summary_date_from",
        readonly=False,
        related_sudo=True
    )
    summary_latency_inseconds = fields.Integer(
        string='Latencia(segundos)',
        related="company_id.summary_latency_inseconds",
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
