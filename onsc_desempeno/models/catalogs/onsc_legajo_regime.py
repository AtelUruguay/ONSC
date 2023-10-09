# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, tools

_logger = logging.getLogger(__name__)


class ONSCLegajoRegime(models.Model):
    _inherit = 'onsc.legajo.regime'
    
    is_desempeno = fields.Boolean(string=u'Desempeño')
