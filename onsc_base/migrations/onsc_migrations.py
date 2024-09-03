# -*- coding: utf-8 -*-

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ONSCMigrations(models.Model):
    _name = 'onsc.migrations'
    _description = 'Migraciones manuales a ambientes'

    def _v27(self, cv_ids=False):
        # onsc_cv_digital 15.0.27.0.0
        BFormation = self.env['onsc.cv.basic.formation'].sudo().with_context(ignore_base_restrict=True,
                                                                             ignore_documentary_status=True)
        AFormation = self.env['onsc.cv.advanced.formation'].sudo().with_context(ignore_base_restrict=True,
                                                                                ignore_documentary_status=True)
        Course = self.env['onsc.cv.course.certificate'].sudo().with_context(ignore_base_restrict=True,
                                                                            ignore_documentary_status=True)
        OtheRelevantInformation = self.env['onsc.cv.other.relevant.information'].sudo().with_context(
            ignore_base_restrict=True, ignore_documentary_status=True)
        ParticipationEvent = self.env['onsc.cv.participation.event'].sudo().with_context(ignore_base_restrict=True,
                                                                                         ignore_documentary_status=True)
        PublicationProductionEvaluation = self.env['onsc.cv.publication.production.evaluation'].sudo().with_context(
            ignore_base_restrict=True, ignore_documentary_status=True)
        TutoringOrientationSupervision = self.env['onsc.cv.tutoring.orientation.supervision'].sudo().with_context(
            ignore_base_restrict=True, ignore_documentary_status=True)
        Voluntariado = self.env['onsc.cv.volunteering'].sudo().with_context(ignore_base_restrict=True,
                                                                            ignore_documentary_status=True)
        WorkExperience = self.env['onsc.cv.work.experience'].sudo().with_context(ignore_base_restrict=True,
                                                                                 ignore_documentary_status=True)
        WorkInvestigation = self.env['onsc.cv.work.investigation'].sudo().with_context(ignore_base_restrict=True,
                                                                                       ignore_documentary_status=True)
        WorkTeaching = self.env['onsc.cv.work.teaching'].sudo().with_context(ignore_base_restrict=True,
                                                                             ignore_documentary_status=True)

        args = [
            ('cv_digital_id.is_docket_active', '=', True),
            ('cv_digital_id.type', '=', 'cv'),
            ('documentary_validation_state', '=', 'validated')
        ]
        course_args = [
            ('cv_digital_id.is_docket_active', '=', True),
            ('cv_digital_id.type', '=', 'cv'),
            ('documentary_validation_state', '=', 'validated'),
            ('record_type', '=', 'course')
        ]
        if cv_ids:
            args.append(('cv_digital_id.id', 'in', cv_ids))
            course_args.append(('cv_digital_id.id', 'in', cv_ids))

        for record in BFormation.search(args):
            record.set_legajo_validated_records()
        for record in AFormation.search(args):
            record.set_legajo_validated_records()
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

        _logger.info("FIN CARGA DE SECCIONES VALIDADAS")
        return True

    def _v28_5(self, cv_ids=False):
        Course = self.env['onsc.cv.course.certificate'].sudo().with_context(ignore_base_restrict=True,
                                                                            ignore_documentary_status=True)
        course_args = [
            ('cv_digital_id.is_docket_active', '=', True),
            ('cv_digital_id.type', '=', 'cv'),
            ('documentary_validation_state', '=', 'validated'),
        ]
        for record in Course.search(course_args):
            record.set_legajo_validated_records()

        _logger.info("FIN CARGA DE SECCIONES VALIDADAS")
        return True
