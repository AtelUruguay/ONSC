# -*- coding: utf-8 -*-

from odoo import models


class ONSCMigrations(models.Model):
    _name = 'onsc.migrations'
    _description = 'Migraciones manuales a ambientes'

    def _v27(self):
        # onsc_cv_digital 15.0.27.0.0
        BFormation = self.env['onsc.cv.basic.formation'].sudo().with_context(ignore_base_restrict=True)
        AFormation = self.env['onsc.cv.advanced.formation'].sudo().with_context(ignore_base_restrict=True)
        Course = self.env['onsc.cv.course.certificate'].sudo().with_context(ignore_base_restrict=True)
        OtheRelevantInformation = self.env['onsc.cv.other.relevant.information'].sudo().with_context(
            ignore_base_restrict=True)
        ParticipationEvent = self.env['onsc.cv.participation.event'].sudo().with_context(ignore_base_restrict=True)
        PublicationProductionEvaluation = self.env['onsc.cv.publication.production.evaluation'].sudo().with_context(
            ignore_base_restrict=True)
        TutoringOrientationSupervision = self.env['onsc.cv.tutoring.orientation.supervision'].sudo().with_context(
            ignore_base_restrict=True)
        Voluntariado = self.env['onsc.cv.volunteering'].sudo().with_context(ignore_base_restrict=True)
        WorkExperience = self.env['onsc.legajo.work.experience'].sudo().with_context(ignore_base_restrict=True)
        WorkInvestigation = self.env['onsc.cv.work.investigation'].sudo().with_context(ignore_base_restrict=True)
        WorkTeaching = self.env['onsc.cv.work.teaching'].sudo().with_context(ignore_base_restrict=True)

        args = [
            ('cv_digital_id.is_docket_active', '=', True),
            ('cv_digital_id.type', '=', 'cv'),
            ('documentary_validation_state', '=', 'validated')
        ]

        for record in BFormation.search(args):
            record.set_legajo_validated_records()
        for record in AFormation.search(args):
            record.set_legajo_validated_records()
        course_args = args
        course_args.append(('record_type', '=', 'course'))
        for record in Course.search(course_args):
            record.set_legajo_validated_records()
        for record in OtheRelevantInformation.search(args):
            record.set_legajo_validated_records()
        for record in ParticipationEvent.search(args):
            record.set_legajo_validated_records()
        for record in PublicationProductionEvaluation.search(args):
            record.set_legajo_validated_records()
        for record in TutoringOrientationSupervision.search(args):
            record.set_legajo_validated_records()
        for record in Voluntariado.search(args):
            record.set_legajo_validated_records()
        for record in WorkExperience.search(args):
            record.set_legajo_validated_records()
        for record in WorkInvestigation.search(args):
            record.set_legajo_validated_records()
        for record in WorkTeaching.search(args):
            record.set_legajo_validated_records()

        return True
