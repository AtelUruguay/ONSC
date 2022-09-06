# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from .abstracts.onsc_cv_abstract_config import STATES as CONDITIONAL_VALIDATION_STATES
from ..soap import soap_error_codes

_logger = logging.getLogger(__name__)


class ONSCCVDigitalCall(models.Model):
    _name = 'onsc.cv.digital.call'
    _inherits = {'onsc.cv.digital': 'cv_digital_id'}
    _description = 'Llamado'
    _rec_name = 'cv_full_name'

    cv_digital_id = fields.Many2one(
        "onsc.cv.digital",
        string="CV interno",
        auto_join=True,
        required=True,
        index=True)

    cv_digital_origin_id = fields.Many2one(
        "onsc.cv.digital",
        string="CV",
        ondelete='set null',
        index=True)

    call_number = fields.Char(string=u"Llamado", required=True, index=True)
    postulation_date = fields.Datetime(string=u"Fecha de postulación", required=True, index=True)
    postulation_number = fields.Char(string=u"Número de postulación", required=True, index=True)
    is_json_sent = fields.Boolean(string="Copia enviada", default=False)
    is_cancel = fields.Boolean(string="Cancelado")
    is_zip = fields.Boolean(string="ZIP generado")
    is_trans = fields.Boolean(string=u"Personas Trans (Art.12 Ley N° 19.684)")
    is_afro = fields.Boolean(string=u"Afrodescendientes (Art.4 Ley N° 19122)")
    is_disabilitie = fields.Boolean(string=u"Persona con Discapacidad (Art. 49 Ley N° 18.651)")
    is_victim = fields.Boolean(string=u"Personas víctimas de delitos violentos (Art. 105 Ley N° 19.889)")
    preselected = fields.Selection(string="Preseleccionado", selection=[('yes', 'Si'), ('no', 'No')])

    call_conditional_state = fields.Selection(
        string="Estado de valores condicionales",
        selection=CONDITIONAL_VALIDATION_STATES,
        compute='_compute_call_conditional_state', store=True)

    @api.constrains("cv_digital_id", "cv_digital_id.active", "call_number", "cv_digital_origin_id")
    def _check_cv_call_unicity(self):
        for record in self.filtered(lambda x: x.active):
            if self.search_count([
                ('active', '=', True),
                ('cv_digital_origin_id', '=', record.cv_digital_origin_id.id),
                ('call_number', '=', record.call_number),
                ('id', '!=', record.id)]):
                raise ValidationError(
                    _(u"El CV ya se encuentra activo para este llamado")
                )

    def init(self):
        self._cr.execute("""
            CREATE INDEX IF NOT EXISTS onsc_cv_digital_call_postulation_number
                                    ON onsc_cv_digital_call (call_number,postulation_number)
        """)

    @api.depends(
        'cv_address_state',
        'basic_formation_ids.conditional_validation_state',
        'advanced_formation_ids.conditional_validation_state',
        'course_ids.conditional_validation_state',
        'certificate_ids.conditional_validation_state',
        'work_experience_ids.conditional_validation_state',
        'work_teaching_ids.conditional_validation_state',
        'work_investigation_ids.conditional_validation_state',
        'tutoring_orientation_supervision_ids.conditional_validation_state',
        'participation_event_ids.conditional_validation_state',
    )
    def _compute_call_conditional_state(self):
        _sql = '''
SELECT SUM(count) FROM
(
SELECT COUNT(conditional_validation_state) FROM onsc_cv_course_certificate WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_participation_event WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_experience WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_basic_formation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_advanced_formation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_tutoring_orientation_supervision WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_experience WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_teaching WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
UNION ALL
SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_investigation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
) AS conditional_state
        '''
        for record in self.filtered(lambda x: x.is_json_sent is False):
            self.env.cr.execute(_sql % (record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id,
                                        record.cv_digital_id.id))
            result = self.env.cr.dictfetchone()
            if not result or result['sum'] > 0 or record.cv_address_state == 'to_validate':
                record.call_conditional_state = 'to_validate'
            else:
                record.call_conditional_state = 'validated'

    @api.model
    def create(self, values):
        values['type'] = 'call'
        result = super(ONSCCVDigitalCall, self).create(values)
        return result

    @api.model
    def _create_postulation(self,
                            country_code,
                            doc_type_code,
                            doc_number,
                            postulation_date,
                            postulation_number,
                            call_number,
                            accion,
                            ):
        if len(country_code) != 2:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_151_1)
        country_id = self.env['res.country'].search([('code', '=', country_code)], limit=1)
        if not country_id:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_151)
        doc_type_id = self.env['onsc.cv.document.type'].search([('code', '=', doc_type_code)], limit=1)
        if not doc_type_id:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_152)
        if not isinstance(accion, str) or accion not in ['P', 'R', 'C']:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_154)

        cv_digital_id = self.env['onsc.cv.digital'].search([
            ('cv_emissor_country_id', '=', country_id.id),
            ('cv_document_type_id', '=', doc_type_id.id),
            ('cv_nro_doc', '=', doc_number),
            ('type', '=', 'cv')
        ], limit=1)
        if not cv_digital_id:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_153)

        if accion == 'P':
            return self._postulate(cv_digital_id, call_number, postulation_date, postulation_number)
        elif accion == 'R':
            return self._repostulate(cv_digital_id, call_number, postulation_date, postulation_number)
        elif accion == 'C':
            return self._cancel_postulation(cv_digital_id, call_number)
        return True

    def _postulate(self, cv_digital_id, call_number, postulation_date, postulation_number):
        new_cv_digital = cv_digital_id.copy({
            'type': 'call'
        })
        cv_call = self.env['onsc.cv.digital.call'].create({
            'cv_digital_id': new_cv_digital.id,
            'cv_digital_origin_id': cv_digital_id.id,
            'call_number': call_number,
            'postulation_date': postulation_date,
            'postulation_number': postulation_number,
        })
        return cv_call

    def _repostulate(self, cv_digital_id, call_number, postulation_date, postulation_number):
        cv_calls = self.search([
            ('cv_digital_origin_id', '=', cv_digital_id.id),
            ('call_number', '=', call_number),
        ])
        if not cv_calls:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_155)
        cv_calls.write({'active': False})
        return self._postulate(cv_digital_id, call_number, postulation_date, postulation_number)

    def _cancel_postulation(self, cv_digital_id, call_number):
        cv_calls = self.search([
            ('cv_digital_origin_id', '=', cv_digital_id.id),
            ('call_number', '=', call_number),
        ])
        if not cv_calls:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_155)
        cv_calls.write({'active': False, 'is_cancel': True})
