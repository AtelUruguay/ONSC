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

    def _v28_6(self):
        Evaluation = self.env['onsc.desempeno.evaluation'].suspend_security()
        _logger.info('CRON 28.6')
        for evaluation in Evaluation.with_context(ignore_security_rules=True).search([
            ('evaluation_type', '=', 'collaborator'),
        ]):
            if evaluation.uo_id.id != evaluation.evaluator_uo_id.id:
                _logger.info('INFO EVALUACION: %s, EVALUADOR: %s, EVALUADO: %s, UO_ACTUAL: %s,%s, UO_NUEVA: %s,%s' % (
                    evaluation.id,
                    evaluation.evaluator_id.display_name,
                    evaluation.evaluated_id.display_name,
                    evaluation.uo_id.id,
                    evaluation.uo_id.display_name,
                    evaluation.evaluator_uo_id.id,
                    evaluation.evaluator_uo_id.display_name,
                ))
                evaluation.write({'uo_id': evaluation.evaluator_uo_id.id})
        _logger.info('FIN CRON 28.6')
        return True

    def _v28_7_altaVL(self, date=False, id=False):
        _logger.info('CRON 28.7 ALTAVL')
        AltaVL = self.env['onsc.legajo.alta.vl'].sudo().with_context(ignore_base_restrict=True)
        if date:
            args = [('create_date', '>=', date)]
        elif id:
            args = [('id', '>=', id)]
        else:
            return
        cv_digitals = AltaVL.search(args).mapped('cv_digital_id')
        _logger.info('CVS: %s' % (str(cv_digitals.ids)))
        self._v27(cv_digitals.ids)
        _logger.info('FIN CRON 28.7 ALTAVL')

    def _v28_7_altaCS(self, date=False, id=False):
        _logger.info('CRON 28.7 ALTACS')
        AltaCS = self.env['onsc.legajo.alta.cs'].sudo().with_context(ignore_base_restrict=True)
        CvDigital = self.env['onsc.cv.digital'].sudo()
        if date:
            args = [('create_date', '>=', date)]
        elif id:
            args = [('id', '>=', id)]
        else:
            return
        partners = AltaCS.search(args).mapped('partner_id')
        cv_digitals = CvDigital.search([('partner_id', 'in', partners.ids), ('type', '=', 'cv')])

        _logger.info('CVS: %s' % (str(cv_digitals.ids)))
        self._v27(cv_digitals.ids)
        _logger.info('FIN CRON 28.7 ALTACS')

    def _v28_8_bajaVL(self):
        _logger.info('CRON 28.8 bajaVL')
        BajaVL = self.env['onsc.legajo.baja.vl'].sudo().with_context(ignore_base_restrict=True)
        bajasVL_towrite = self.env['onsc.legajo.baja.vl']
        for bajaVl in BajaVL.search([('state', 'in', ['borrador','error_sgh'])]):
            if not bajaVl.is_require_extended and bajaVl.causes_discharge_extended_id:
                bajasVL_towrite |= bajaVl
        bajasVL_towrite.write({'causes_discharge_extended_id': False})
        bajasVL_towrite._compute_is_read_only_description()
        _logger.info('FIN CRON 28.8 bajaVL')

    def _ler_2_1_01(self, lote=1, lote_size=1000):
        StateTransactionHistory = self.env['hr.contract.state.transaction.history'].suspend_security()
        HrContract = self.env['hr.contract'].sudo()
        _lote = lote - 1
        offset = lote_size * _lote
        legajo_state_field_id = self.env['ir.model.fields'].search([
            ('model', '=', 'hr.contract'),
            ('name', '=', 'legajo_state')
        ], limit=1)
        legajo_state_items= dict(HrContract.fields_get(allfields=['legajo_state'])['legajo_state']['selection']).items()
        messages = self.env['mail.message'].sudo().search([
            ('model', '=', 'hr.contract'),
            ('tracking_value_ids.field', '=', legajo_state_field_id.id),
        ], order='res_id asc, date asc', limit=lote_size, offset=offset)
        bulked_vals = []
        for msg in messages:
            if HrContract.search_count([('id', '=', msg.res_id)]):
                if len(msg.tracking_value_ids) > 1:
                    tracking_value_id = msg.tracking_value_ids.filtered(lambda x: x.field.id == legajo_state_field_id.id)
                else:
                    tracking_value_id = msg.tracking_value_ids
                from_state_key = next(key for key, value in legajo_state_items if value == tracking_value_id.old_value_char)
                to_state_key = next(key for key, value in legajo_state_items if value == tracking_value_id.new_value_char)
                bulked_vals.append({
                    'contract_id': msg.res_id,
                    'transaction_date': msg.date,
                    'from_state': from_state_key,
                    'to_state': to_state_key,
                })
        StateTransactionHistory.create(bulked_vals)

    def _ler_2_1_01_contract(self, lote=1, lote_size=1000):
        HrContract = self.env['hr.contract'].sudo()
        StateTransactionHistory = self.env['hr.contract.state.transaction.history'].suspend_security()
        _lote = lote - 1
        offset = lote_size * _lote
        bulked_vals = []
        for contract in HrContract.search([], limit=lote_size, offset=offset):
            first_history = StateTransactionHistory.search([('contract_id', '=', contract.id)], limit=1)
            if first_history:
                to_state = first_history.from_state
            else:
                to_state = contract.legajo_state
            bulked_vals.append({
                'contract_id': contract.id,
                'transaction_date': contract.create_date,
                'to_state': to_state,
            })
        StateTransactionHistory.create(bulked_vals)
