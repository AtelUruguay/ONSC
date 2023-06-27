# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVSettings(models.TransientModel):
    _name = 'onsc.cv.settings'
    _description = u"Configuración"

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    cv_help_general_info = fields.Char(related="company_id.cv_help_general_info", readonly=False, related_sudo=True)
    cv_help_address = fields.Char(related="company_id.cv_help_address", readonly=False, related_sudo=True)
    cv_help_work_experience = fields.Char(related="company_id.cv_help_work_experience", readonly=False, related_sudo=True)
    cv_help_work_teaching = fields.Char(related="company_id.cv_help_work_teaching", readonly=False, related_sudo=True)
    cv_help_work_investigation = fields.Char(related="company_id.cv_help_work_investigation", readonly=False, related_sudo=True)
    cv_help_formation = fields.Char(related="company_id.cv_help_formation", readonly=False, related_sudo=True)
    cv_help_course_certificate = fields.Char(related="company_id.cv_help_course_certificate", readonly=False, related_sudo=True)
    cv_help_volunteering = fields.Char(related="company_id.cv_help_volunteering", readonly=False, related_sudo=True)
    cv_help_language_level = fields.Char(related="company_id.cv_help_language_level", readonly=False, related_sudo=True)
    cv_help_publications_productions_evaluations = fields.Char(
        related="company_id.cv_help_publications_productions_evaluations", readonly=False, related_sudo=True)
    cv_help_tutoring_orientation_supervision = fields.Char(
        related="company_id.cv_help_tutoring_orientation_supervision", readonly=False, related_sudo=True)
    cv_help_disability = fields.Char(related="company_id.cv_help_disability", readonly=False, related_sudo=True)
    cv_help_participation_event = fields.Char(related="company_id.cv_help_participation_event", readonly=False, related_sudo=True)
    cv_help_other_relevant_information = fields.Char(related="company_id.cv_help_other_relevant_information",
                                                     readonly=False, related_sudo=True)
    cv_help_reference = fields.Char(
        related="company_id.cv_help_reference", readonly=False, related_sudo=True)

    is_cv_user_acceptance_active = fields.Boolean(
        related="company_id.is_cv_user_acceptance_active", readonly=False, related_sudo=True)
    cv_user_acceptance = fields.Text(
        related="company_id.cv_user_acceptance", readonly=False, related_sudo=True)

    def execute(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def write(self, vals):
        res = super(ONSCCVSettings, self.suspend_security()).write(vals)
        return res
