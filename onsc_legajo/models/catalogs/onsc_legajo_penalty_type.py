# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

SINOSELECTION = [
    ('S', 'S'),
    ('N', 'N'),
]


class ONSCLegajoRegime(models.Model):
    _name = 'onsc.legajo.penalty.type'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Tipo de sanción'

    code = fields.Char(string=u"Código", required=True)
    subcode = fields.Char(string=u"Subcódigo", required=True)
    description = fields.Char(string="Descripción", required=True)
    warning = fields.Selection(SINOSELECTION, string="Advertencia en Alta VL (S/N)")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('cod_uniq', 'unique("code")', u'El código debe ser único'),
        ('descripcion_uniq', 'unique("description")', u'La descripción debe ser única')
    ]
