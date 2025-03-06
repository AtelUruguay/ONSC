# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

SNSELECTION = [
    ('s', 'S'),
    ('n', 'N'),
]


class ONSCLegajoRegime(models.Model):
    _name = 'onsc.legajo.penalty.type'
    _inherit = 'onsc.legajo.abstract.sync'
    _description = 'Tipo de sanción'

    identifier = fields.Char(string='ID', required=True)
    code = fields.Char(string=u"Código", required=True)
    subcode = fields.Char(string=u"Subcódigo", required=True)
    description = fields.Char(string="Descripción", required=True)
    warning = fields.Selection(SNSELECTION, string="Advertencia en Alta VL (S/N)")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('identifier_uniq', 'unique(identifier)', u'El ID debe ser único'),
        ('cod_uniq', 'unique(code,subcode)', u'La combinación Código-Subcódigo debe ser única'),
    ]
