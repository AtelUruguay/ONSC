# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Borrador'),
    ('in_process', 'En Proceso'),
    ('completed', 'Completado'),
    ('finished', 'Finalizado'),
    ('uncompleted', 'Sin Finalizar'),
    ('canceled', 'Cancelado'),
    ('deal_close', "Acuerdo cerrado")
]

HTML_HELP = """<a class="btn" style="padding-top:inherit!important;" target="_blank" title="%s"><i class="fa fa-question-circle-o" role="img" aria-label="Info"/></a>"""


class ONSCDesempenoEvaluationCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.competency'
    _description = u'Competencia'
    _order = "skill_id"

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    consolidate_id = fields.Many2one('onsc.desempeno.consolidated', string='Competencia', readonly=True)
    gap_deal_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    state = fields.Selection(STATE, string='Estado', related='evaluation_id.state', readonly=True)
    state_deal = fields.Selection(STATE, string='Estado', related='gap_deal_id.state', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    skill_line_ids = fields.Many2many(
        comodel_name="onsc.desempeno.skill.line",
        relation="competency_skill_line_rel",
        string="Lineas de competencia")
    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo',
                                required=False, ondelete='restrict')
    improvement_areas = fields.Text(string='Brecha/Fortalezas/Aspectos a mejorar', required=False,
                                    help='Para identificar la necesidad de desarrollo que requiere la persona, '
                                         'compare, para cada competencia, el desempeño observado con los '
                                         'comportamientos esperados, contenidos en las dimensiones de '
                                         'cada competencia.')
    evaluation_form_edit = fields.Boolean('Puede editar el form?', related='evaluation_id.evaluation_form_edit', )
    order = fields.Integer('Orden')
    locked = fields.Boolean('Bloqueado', related='evaluation_id.locked')

    skill_tooltip = fields.Html(
        compute=lambda s: s._get_help('skill_tooltip'),
        default=lambda s: s._get_help('skill_tooltip', True))
    competency_form_edit = fields.Boolean('Puede editar el form?', compute='_compute_competency_form_edit')

    @api.depends('state', 'state_deal')
    def _compute_competency_form_edit(self):
        for record in self:
            if record.gap_deal_id:
                record.competency_form_edit = record.gap_deal_id.gap_deal_state != 'no_deal' or record.gap_deal_id.state != 'in_process'
            else:
                record.competency_form_edit = record.state != 'in_process'

    def _get_help(self, help_field='', is_default=False):
        _html2construct = HTML_HELP % ('Tooltip')
        if is_default:
            return eval("_html2construct")
        for rec in self:
            _html2construct = HTML_HELP % (rec.suspend_security().skill_id.definition or '')
            setattr(rec, help_field, _html2construct)

    def button_open_current_skill(self):
        action = self.sudo().env.ref('onsc_desempeno.onsc_desempeno_competency_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def action_close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
