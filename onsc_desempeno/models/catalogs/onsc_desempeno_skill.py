# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

HTML_HELP = """<a class="btn" target="_blank" title="%s"><i class="fa fa-question-circle-o" role="img" aria-label="Info"/></a>"""


class ONSCDesempenoSkill(models.Model):
    _name = 'onsc.desempeno.skill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Competencias'
    _order = "name"

    name = fields.Char(string="Nombre de la competencia", required=True)
    definition = fields.Text(string="Definición")
    active = fields.Boolean(string="Activo", tracking=True, default=True)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)
    skill_line_ids = fields.One2many("onsc.desempeno.skill.line", inverse_name="skill_id",
                                     string="Lineas de competencia")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'El nombre de la competencia debe ser único'),
    ]

    @api.constrains("skill_line_ids")
    def _check_skill_line_ids(self):
        for record in self:
            if not record.skill_line_ids:
                raise ValidationError(_("Debe haber al menos una dimension"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = _("%s (Copia)") % self.name
        return super(ONSCDesempenoSkill, self).copy(default=default)


class ONSCDesempenoSkillLine(models.Model):
    _name = 'onsc.desempeno.skill.line'
    _description = 'Competencias linea'
    _order = 'name_dimension, name_level'

    dimension_id = fields.Many2one('onsc.desempeno.dimension', string="Dimensión",
                                   required=True, ondelete='restrict')
    level_id = fields.Many2one('onsc.desempeno.level', string="Nivel", required=True, ondelete='restrict')
    behavior = fields.Char(string="Comportamiento esperado", required=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string="Competencias", required=True, ondelete='cascade')
    name_dimension = fields.Char(string="Competencias", related='dimension_id.name', store=True)
    name_level = fields.Char(string="Nivel", related='level_id.name', store=True)
    competency_id = fields.Many2one('onsc.desempeno.evaluation.competency', string="Competencias")
    dimension_tooltip = fields.Html(string=" ",
                                    compute=lambda s: s._get_help('dimension_tooltip'),
                                    default=lambda s: s._get_help('dimension_tooltip', True))

    def _get_help(self, help_field='', is_default=False):
        _html2construct = HTML_HELP % ('Tooltip')
        if is_default:
            return eval("_html2construct")
        for rec in self:
            _html2construct = HTML_HELP % (rec.sudo().dimension_id.definition or '')
            setattr(rec, help_field, _html2construct)


class ONSCDesempenoEvaluationSkillLine(models.Model):
    _name = 'onsc.desempeno.evaluation.skill.line'
    _inherit = 'onsc.desempeno.skill.line'

    frequency_id = fields.Many2one(
        'onsc.desempeno.frequency.equivalence',
        string="Frecuencia del comportamiento esperado")
