# -*- coding: utf-8 -*-

from odoo import fields, models

DNIC_DOC_TYPE = [
    ('DO', 'DO')
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    cv_help_general_info = fields.Char('Información General')
    cv_help_address = fields.Char('Domicilio')
    cv_help_work_experience = fields.Char('Experiencia laboral')
    cv_help_work_teaching = fields.Char('Docencia')
    cv_help_work_investigation = fields.Char('Investigación')
    cv_help_formation = fields.Char('Formación')
    cv_help_course_certificate = fields.Char('Cursos y certificado')
    cv_help_volunteering = fields.Char('Voluntariado')
    cv_help_language_level = fields.Char('Idiomas')
    cv_help_publications_productions_evaluations = fields.Char('Publicaciones, Producciones y Evaluaciones')
    cv_help_tutoring_orientation_supervision = fields.Char('Tutorías, Orientaciones, Supervisiones')
    cv_help_disability = fields.Char('Discapacidad')
    cv_help_participation_event = fields.Char('Participación en eventos')
    cv_help_other_relevant_information = fields.Char('Otra información relevante')
    cv_help_reference = fields.Char('Referencias')

    is_rve_integrated = fields.Boolean(u'Integración con RVE')
    rve_wsdl = fields.Char('URL del WSDL')

