# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCLog(models.Model):
    _name = 'onsc.log'
    _description = 'Bandeja de logs ONSC'
    _order = "create_date DESC"


    process = fields.Char(string="Proceso", required=True, index=True)
    origin = fields.Char(string='Origen', required=True, index=True)
    type = fields.Selection(
        string='Tipo',
        selection=[("info", "Info"), ("warning", "Alerta"), ("error", "Error")],
        default="info",
        index=True,
        required=True
    )
    create_date = fields.Datetime(string=u'Fecha', index=True)
    ref = fields.Char(string='Referencia', required=True, index=True)
    code = fields.Char(string='Código', required=True, readonly=True)
    description = fields.Char(string='Descripción', readonly=True)
    long_description = fields.Text(string='Detalle', readonly=True)
