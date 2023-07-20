# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoSkill(models.Model):
    _name = 'onsc.desempeno.skill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Competencias'

    name = fields.Char(string="Competencias", required=True)
    definition = fields.Char(string="Definición de la competencia")
    active = fields.Boolean(string="Activo", tracking=True, default=True)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)
    dimension_id = fields.Many2one('onsc.desempeno.dimension', string="Dimensión", required=True)
    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel", required=True)
    behavior = fields.Char(string="Comportamiento esperado", required=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la competencia debe ser único'),
    ]

    def toggle_active(self):
        return super(ONSCDesempenoSkill, self.with_context(no_check_write=True)).toggle_active()
