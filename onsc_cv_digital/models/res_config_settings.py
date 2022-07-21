# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cv_help_general_info = fields.Char(related="company_id.cv_help_general_info", readonly=False)
    cv_help_address = fields.Char(related="company_id.cv_help_address", readonly=False)
    cv_help_work_experience = fields.Char(related="company_id.cv_help_work_experience", readonly=False)
    cv_help_work_teaching = fields.Char(related="company_id.cv_help_work_teaching", readonly=False)
    cv_help_work_investigation = fields.Char(related="company_id.cv_help_work_investigation", readonly=False)
    cv_help_formation = fields.Char(related="company_id.cv_help_formation", readonly=False)
    cv_help_course_certificate = fields.Char(related="company_id.cv_help_course_certificate", readonly=False)
    cv_help_volunteering = fields.Char(related="company_id.cv_help_volunteering", readonly=False)
    cv_help_language_level = fields.Char(related="company_id.cv_help_language_level", readonly=False)
    cv_help_publications_productions_evaluations = fields.Char(
        related="company_id.cv_help_publications_productions_evaluations", readonly=False)
    cv_help_tutoring_orientation_supervision = fields.Char(
        related="company_id.cv_help_tutoring_orientation_supervision", readonly=False)
    cv_help_disability = fields.Char(related="company_id.cv_help_disability", readonly=False)
    cv_help_participation_event = fields.Char(related="company_id.cv_help_participation_event", readonly=False)
    cv_help_other_relevant_information = fields.Char(related="company_id.cv_help_other_relevant_information",
                                                     readonly=False)
