# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class ONSCDesempenoSkill(models.Model):
    _name = 'onsc.desempeno.skill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Competencias'

    name = fields.Char(string="Nombre de la competencia", required=True)
    definition = fields.Char(string="Definición")
    active = fields.Boolean(string="Activo", tracking=True, default=True)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)
    skill_line_ids = fields.One2many("onsc.desempeno.skill.line", inverse_name="skill_id",
                                      string="Lineas de competencia")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la competencia debe ser único'),
    ]

    def toggle_active(self):
        return super(ONSCDesempenoSkill, self.with_context(no_check_write=True)).toggle_active()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoSkill, self).copy(default=default)


class ONSCDesempenoSkillLine(models.Model):
    _name = 'onsc.desempeno.skill.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Competencias linea'

    dimension_id = fields.Many2one('onsc.desempeno.dimension', string="Dimensión", required=True)
    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel", required=True)
    behavior = fields.Char(string="Comportamiento esperado", required=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string="Competencias", required=True)

    _sql_constraints = [
        ('line_uniq', 'unique(skill_id,dimension_id,level_id)',
         u'La dimensión y nivel debe ser unico para la competencia'),
    ]
