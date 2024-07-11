# -*- coding: utf-8 -*-
from odoo import models


class ONSCLegajoReportConfigSeccion(models.Model):
    _name = 'onsc.legajo.report.config.seccion'
    _inherit = 'onsc.cv.report.config.seccion'
    _rec_name = 'seccion'
    _description = 'Configuración reporte Legajo'
