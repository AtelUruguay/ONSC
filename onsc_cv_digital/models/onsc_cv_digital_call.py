# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from .abstracts.onsc_cv_abstract_config import STATES as CONDITIONAL_VALIDATION_STATES
from .abstracts.onsc_cv_abstract_documentary_validation import DOCUMENTARY_VALIDATION_STATES
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
    postulation_date = fields.Datetime(string=u"Fecha de actualización", required=True, index=True)
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

    gral_info_documentary_validation_state = fields.Selection(
        selection=DOCUMENTARY_VALIDATION_STATES,
        string="Estado de validación documental",
        compute='_compute_gral_info_documentary_validation_state',
        store=True
    )

    address_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    disabilitie_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')
    nro_doc_documentary_validation_state = fields.Selection(
        string="Estado de validación documental",
        selection=DOCUMENTARY_VALIDATION_STATES,
        default='to_validate')

    @api.constrains("cv_digital_id", "cv_digital_id.active", "call_number", "cv_digital_origin_id")
    def _check_cv_call_unicity(self):
        for record in self.filtered(lambda x: x.active):
            if self.search_count([('active', '=', True),
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
        # FIXME codigo sql es mas optimo pero no cubre todas las casuisticas(creacion todavia no esta en base de datos), se pasa a python
        # pylint: disable=sql-injection
        #         _sql = '''
        # SELECT SUM(count) FROM
        # (
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_course_certificate WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_participation_event WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_experience WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_basic_formation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_advanced_formation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_tutoring_orientation_supervision WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_publication_production_evaluation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_teaching WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # UNION ALL
        # SELECT COUNT(conditional_validation_state) FROM onsc_cv_work_investigation WHERE cv_digital_id = %s AND conditional_validation_state = 'to_validate'
        # ) AS conditional_state
        #         '''
        for record in self.filtered(lambda x: x.is_json_sent is False and x.active):
            conditional_validation_state = record.course_certificate_ids.mapped('conditional_validation_state')
            conditional_validation_state.extend(record.participation_event_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.work_experience_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.basic_formation_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.advanced_formation_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.work_teaching_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.work_investigation_ids.mapped('conditional_validation_state'))
            conditional_validation_state.extend(record.participation_event_ids.mapped('conditional_validation_state'))
            conditional_validation_state.append(record.cv_address_state)
            if 'to_validate' in conditional_validation_state:
                record.call_conditional_state = 'to_validate'
            else:
                record.call_conditional_state = 'validated'

            # self.env.cr.execute(_sql % (record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id,
            #                             record.cv_digital_id.id))
            # result = self.env.cr.dictfetchone()
            # if not result or result['sum'] > 0 or record.cv_address_state == 'to_validate':
            #     record.call_conditional_state = 'to_validate'
            # else:
            #     record.call_conditional_state = 'validated'

    def _get_documentary_validation_models(self):
        if not bool(self._context):
            return ['address_documentary_validation_state',
                    'civical_credential_documentary_validation_state',
                    'nro_doc_documentary_validation_state',
                    'disabilitie_documentary_validation_state']
        configs = self.env['onsc.cv.documentary.validation.config'].search([])
        validation_models = ['address_documentary_validation_state',
                             'civical_credential_documentary_validation_state',
                             'nro_doc_documentary_validation_state',
                             'disabilitie_documentary_validation_state']
        for config in configs.filtered(lambda x: x.field_id):
            validation_models.append('%s.documentary_validation_state' % config.field_id.name)
        return validation_models

    # @property
    # def field_documentary_validation_models(self):
    #     configs = self.env['onsc.cv.documentary.validation.config'].search([])
    #     validation_models = ['address_documentary_validation_state',
    #                          'civical_credential_documentary_validation_state',
    #                          'nro_doc_documentary_validation_state',
    #                          'disabilitie_documentary_validation_state']
    #     for config in configs.filtered(lambda x: x.field_id):
    #         validation_models.append('%s.documentary_validation_state' % config.field_id.name)
    #     return validation_models
    #     return [
    #         'work_experience_ids.documentary_validation_state',
    #         'basic_formation_ids.documentary_validation_state',
    #         'advanced_formation_ids.documentary_validation_state',
    #         'course_certificate_ids.documentary_validation_state',
    #         'volunteering_ids.documentary_validation_state',
    #         'work_teaching_ids.documentary_validation_state',
    #         'work_investigation_ids.documentary_validation_state',
    #         'publication_production_evaluation_ids.documentary_validation_state',
    #         'tutoring_orientation_supervision_ids.documentary_validation_state',
    #         'participation_event_ids.documentary_validation_state',
    #         'address_documentary_validation_state',
    #         'disabilitie_documentary_validation_state',
    #     ]

    @api.depends(lambda self: self._get_documentary_validation_models())
    def _compute_gral_info_documentary_validation_state(self):
        field_documentary_validation_models = self._get_documentary_validation_models()
        for record in self.filtered(lambda x: x.is_zip is False):
            _documentary_validation_state = 'validated'
            for documentary_validation_model in field_documentary_validation_models:
                if 'to_validate' in eval("record.mapped('%s')" % documentary_validation_model):
                    _documentary_validation_state = 'to_validate'
                    break
            record.gral_info_documentary_validation_state = _documentary_validation_state

    @api.model
    def create(self, values):
        values['type'] = 'call'
        return super(ONSCCVDigitalCall, self).create(values)

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
            return self._cancel_postulation(cv_digital_id, call_number, postulation_date)
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
        cv_calls.write({'active': False, 'postulation_date': postulation_date})
        return self._postulate(cv_digital_id, call_number, postulation_date, postulation_number)

    def _cancel_postulation(self, cv_digital_id, call_number, postulation_date):
        cv_calls = self.search([
            ('cv_digital_origin_id', '=', cv_digital_id.id),
            ('call_number', '=', call_number),
        ])
        if not cv_calls:
            return soap_error_codes._raise_fault(soap_error_codes.LOGIC_155)
        cv_calls.write({'active': False, 'is_cancel': True, 'postulation_date': postulation_date})
        return cv_calls
