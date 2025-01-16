# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    descriptor1_ids = fields.Many2many('onsc.catalog.descriptor1',
                                       string='Escalafones excluidos', ondelete='restrict')
    is_evaluation_form_active = fields.Boolean('Activar Ayuda para formulario de evaluación')
    evaluation_form_text = fields.Text('Ayuda para formulario de evaluación')
    is_environment_evaluation_form_active = fields.Boolean('Activar ayuda para formulario de definición de entorno')
    environment_evaluation_text = fields.Text('Ayuda para formulario de definición de entorno')
    max_environment_evaluation_forms = fields.Integer(string='Tope de formularios por evaluador')
    max_environment_evaluation_leader_forms = fields.Integer(string='Tope de formularios para lider')
    random_environment_evaluation_forms = fields.Integer(
        string='Cantidad de formularios de entorno a generar por definición')
    days_notification_end_ev = fields.Integer(u"Días para notificar antes de la fecha de fin de evaluación")
    days_gap_deal_eval_creation = fields.Integer(u"Días para la creación de Acuerdos de brecha")
    days_gap_develop_plan_creation = fields.Integer(u"Días para la creación de Plan de desarrollo")
    is_improvement_areas_help_form_active = fields.Boolean('Activar ayuda para formulario de competencias')
    improvement_areas_help_text = fields.Text('Ayuda para formulario de competencias')

    # PUNTAJE
    eval_360_score = fields.Integer(string='Puntaje de Evaluación 360')
    gap_deal_score = fields.Integer(string='Puntaje de Acuerdo de brecha')
    development_plan_score = fields.Integer(string='Puntaje de Plan de desarrollo')
    tracing_plan_score = fields.Integer(string='Puntaje de Seguimiento de Plan de desarrollo')
    tracing_plan_activity_score = fields.Integer(string='Puntaje de Actividad de Seguimiento de Plan de desarrollo')
    notification_pending_text = fields.Text('Aviso de noticaciones pendientes')
    is_notification_pending_form_active = fields.Boolean('Activar aviso para formulario de pendiente de noticar')

    def write(self, vals):
        _fields = [
            "is_evaluation_form_active",
            "evaluation_form_text",
            "is_environment_evaluation_form_active",
            "environment_evaluation_text",
            "descriptor1_ids",
            "days_notification_end_ev",
            "descriptor1_ids",
            "max_environment_evaluation_forms",
            "random_environment_evaluation_forms",
            "days_notification_end_ev",
            "days_gap_deal_eval_creation",
            "days_gap_develop_plan_creation",
            "eval_360_score",
            "gap_deal_score",
            "development_plan_score",
            "tracing_plan_score",
            "tracing_plan_activity_score",
            "notification_pending_text",
            "is_notification_pending_form_active",
            "is_improvement_areas_help_form_active",
            "improvement_areas_help_text"
        ]
        if any(x in vals.keys() for x in _fields):
            return super(ResCompany, self.suspend_security()).write(vals)
        return super(ResCompany, self).write(vals)
