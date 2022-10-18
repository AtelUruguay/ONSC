# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVReportConfigSeccion(models.Model):
    _name = 'onsc.cv.report.config.seccion'
    _rec_name = 'seccion'
    _description = 'Configuración reporte CV - Linea'

    seccion = fields.Char(string="Sección", required=True)
    internal_field = fields.Char(string="Campo interno CV", required=True)
    is_default = fields.Boolean(string="Por defecto", default=True)
