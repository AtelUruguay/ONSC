# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ONSCDesempenoEvaluatioDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.evaluation.development.means'
    _description = u'Medios de desarrollo'

    competency_id = fields.Many2one('onsc.desempeno.evaluation.development.competency', string='Medio de desarrollo',
                                    requiered=True)
    agreed_activities = fields.Text('Actividades acordadas', required=True)
    comments = fields.Text('Comentarios', required=True)
    detail_activities = fields.Text('Detalle de actividades', required=True)
    means_id = fields.Many2one('onsc.desempeno.development.means', string='Medio de desarrollo',
                               required=True)
    means_id = fields.Many2one('onsc.desempeno.development.means', string='Seguimiento del plan de desarrollo',
                               required=True)


class ONSCDesempenoEvaluatioDevelopmentCompetency(models.Model):
    _name = 'onsc.desempeno.evaluation.development.competency'
    _description = u'Competencias'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Competencia', readonly=True)
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    development_goal = fields.Text('Objetivo de desarrollo', required=True)
    development_means_ids = fields.One2many('onsc.desempeno.evaluation.development.means', 'competency_id',
                                            string='Medios de desarrollo')


class ONSCDesempenoEvaluatioDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.evaluation.tracing.plan'
    _description = u'Seguimiento del plan de desarrollo'

    development_means_id = fields.Many2one('onsc.desempeno.evaluation.development.means', string='Medio de desarrollo',
                                    requiered=True)
    tracing_plan_date = fields.Date('Fecha de seguimiento de la actividad', required=True)
    comments = fields.Text('Observaciones')
    degree_progress_id = fields.Many2one('onsc.desempeno.degree.progress', string='Grado de avance',
                               required=True)
