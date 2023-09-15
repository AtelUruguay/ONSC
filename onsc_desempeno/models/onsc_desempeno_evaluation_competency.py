# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Borrador'),
    ('in_progress', 'En Proceso'),
    ('completed', 'Completado'),
    ('finished', 'Finalizado'),
    ('uncompleted', 'Sin Finalizar'),
    ('canceled', 'Cancelado')
]

HTML_HELP = """<a class="btn" style="padding-top:inherit!important;" target="_blank" title="%s"><i class="fa fa-question-circle-o" role="img" aria-label="Info"/></a>"""


class ONSCDesempenoEvaluationCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.competency'
    _description = u'Evaluación'
    _order = "skill_id"

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    skill_line_ids = fields.One2many(comodel_name="onsc.desempeno.skill.line", inverse_name="competency_id",
                                     string="Lineas de competencia")
    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo',
                                required=True, ondelete='restrict')
    improvement_areas = fields.Text(string='Brecha/Fortalezas/Aspectos a mejorar', required=True,
                                    help='Para identificar la necesidad de desarrollo que requiere la persona, '
                                         'compare, para cada competencia, el desempeño observado con los '
                                         'comportamientos esperados, contenidos en las dimensiones de '
                                         'cada competencia.')
    evaluation_form_edit = fields.Boolean('Puede editar el form?', related='evaluation_id.evaluation_form_edit', )

    skill_tooltip = fields.Html(
        compute=lambda s: s._get_help('skill_tooltip'),
        default=lambda s: s._get_help('skill_tooltip', True))

    def _get_help(self, help_field='', is_default=False):
        _html2construct = HTML_HELP % ('Tooltip')
        if is_default:
            return eval("_html2construct")
        for rec in self:
            _html2construct = HTML_HELP % (rec.skill_id.definition or '')
            setattr(rec, help_field, _html2construct)

    def button_open_current_skill(self):
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_competency_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
