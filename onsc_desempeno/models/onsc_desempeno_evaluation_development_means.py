# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class ONSCDesempenoEvaluatioDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.evaluation.development.means'
    _description = u'Medios de desarrollo'


    competency_id = fields.Many2one('onsc.desempeno.evaluation.development.competency', string='Medio de desarrollo', requiered=True)
    agreed_activities = fields.Text('Medio de desarrollo', requierd=True)
    comments = fields.Text('Comentarios', requierd=True)
    detail_activities = fields.Text('Detalle de actividades', requierd=True)
    means_id = fields.Many2one('onsc.desempeno.development.means', string='Medio de desarrollo',
                                    requiered=True)




class ONSCDesempenoEvaluatioDevelopmentMeans(models.Model):
    _name = 'onsc.desempeno.evaluation.development.competency'
    _description = u'Medios de desarrollo'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation.', string='Evaluacion')
    skill_id = fields.Many2one('onsc.desempeno.skill', string='Competencia', readonly=True, ondelete='restrict')
    development_goal = fields.Text('Objetivo de desarrollo', requierd=True)
    development_means_ids = fields.One2many('onsc.desempeno.evaluation.development.means', 'competency_id',
                                            string='Medios de desarrollo')
