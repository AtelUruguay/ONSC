# -*- coding: utf-8 -*-

import logging

from odoo import models, _

_logger = logging.getLogger(__name__)


class ONSCBaseUtils(models.AbstractModel):
    _name = 'onsc.base.utils'
    _description = 'Base utils ONSC'

    def _get_catalog_id(self, Catalog, catalog_field, operation, operation_code, log_list):
        """
        Get the catalog ID based on the given operation code.
        :param Catalog: Env of Object. Ex: self.env['catalog']
        :param catalog_field: Field name of the catalog. Ex: 'code'
        :param operation: Record of the operation
        :param operation_code: Var name of the operation. Ex: 'tipo_doc'
        :param log_list: Log list to append errors
        :return: id or False
        """
        if not hasattr(operation, operation_code):
            return False
        int_valid_op = isinstance(getattr(operation, operation_code), int)
        char_valid_op = isinstance(getattr(operation, operation_code), str) and getattr(operation, operation_code) != ""
        if int_valid_op or char_valid_op:
            recordset = Catalog.search([(catalog_field, '=', getattr(operation, operation_code))], limit=1)
            if not recordset:
                log_list.append(_('No se encontró en el catálogo %s el valor %s') % (
                    Catalog._description, getattr(operation, operation_code)))
            return recordset.id
        return False

    def get_really_values_changed(self, recordset, values):
        """
        FILTRA DE TODOS LOS VALORES QUE SE MANDAN A CAMBIAR EN UN RECORDSET CUALES REALMENTE TIENEN DIFERENCIA
        :param recordset: Recordet a evaluar
        :param values: Dict of values, ejemplo: los que vienen en un write
        :return: Dict of values: los que realmente cambiaron
        """
        values_filtered = {}
        _fields_get = recordset.fields_get()
        for key, value in values.items():
            field_type = _fields_get.get(key).get('type')
            if field_type in ('integer', 'binary', 'date', 'datetime'):
                eval_str = "recordset.%s"
            elif field_type == 'many2one':
                eval_str = "recordset.%s.id"
            elif field_type in ['many2many', 'one2many']:
                eval_str = "recordset.%s.ids"
            else:
                eval_str = "recordset.%s"
            if eval(eval_str % (key)) != value:
                values_filtered.update({key: value})
        return values_filtered


class ONSCTools(models.AbstractModel):
    _name = 'onsc.tools'
    _description = 'Base tools ONSC'

    def _20_5_postulations_fix(self, create_date, calls_number_tofix=False):
        # METODO PARA CORREGIR DATOS PROVOCADOS POR EL BUG PS07 12480 Error en Producción- No trae valor de credencial para validar
        # LIBERADO EN LA release/v20.6.1
        Calls = self.env['onsc.cv.digital.call'].suspend_security()
        args = [('create_date', '>=', create_date), ('country_of_birth_id', '=', False)]
        if calls_number_tofix:
            args.append(('call_number', 'in', calls_number_tofix))
        calls = Calls.search(args)
        for call in calls:
            if call.cv_digital_origin_id and call.cv_digital_id:
                cv_digital_id = call.cv_digital_origin_id
                call.cv_digital_id.with_context(
                    no_update_header_documentary_validation=True,
                    no_update_employee_status=True
                ).write({
                    'type': 'call',
                    'document_identity_file': cv_digital_id.document_identity_file,
                    'document_identity_filename': cv_digital_id.document_identity_filename,
                    'country_of_birth_id': cv_digital_id.country_of_birth_id.id,
                    'marital_status_id': cv_digital_id.marital_status_id.id,
                    'uy_citizenship': cv_digital_id.uy_citizenship,
                    'crendencial_serie': cv_digital_id.crendencial_serie,
                    'credential_number': cv_digital_id.credential_number,
                    'civical_credential_file': cv_digital_id.civical_credential_file,
                    'civical_credential_filename': cv_digital_id.civical_credential_filename,
                    'cjppu_affiliate_number': cv_digital_id.cjppu_affiliate_number,
                    'professional_resume': cv_digital_id.professional_resume,
                    'user_linkedIn': cv_digital_id.user_linkedIn,
                    'is_driver_license': cv_digital_id.is_driver_license,
                    'cv_gender_id': cv_digital_id.cv_gender_id.id,
                    'cv_gender2': cv_digital_id.cv_gender2,
                    'cv_gender_record_file': cv_digital_id.cv_gender_record_file,
                    'cv_gender_record_filename': cv_digital_id.cv_gender_record_filename,
                    'is_cv_gender_public': cv_digital_id.is_cv_gender_public,
                    'is_cv_gender_record': cv_digital_id.is_cv_gender_record,
                    'cv_race2': cv_digital_id.cv_race2,
                    'is_cv_race_public': cv_digital_id.is_cv_race_public,
                    'is_afro_descendants': cv_digital_id.is_afro_descendants,
                    'afro_descendants_file': cv_digital_id.afro_descendants_file,
                    'afro_descendants_filename': cv_digital_id.afro_descendants_filename,
                    'is_occupational_health_card': cv_digital_id.is_occupational_health_card,
                    'occupational_health_card_date': cv_digital_id.occupational_health_card_date,
                    'occupational_health_card_file': cv_digital_id.occupational_health_card_file,
                    'occupational_health_card_filename': cv_digital_id.occupational_health_card_filename,
                    'is_medical_aptitude_certificate_status': cv_digital_id.is_medical_aptitude_certificate_status,
                    'medical_aptitude_certificate_date': cv_digital_id.medical_aptitude_certificate_date,
                    'medical_aptitude_certificate_file': cv_digital_id.medical_aptitude_certificate_file,
                    'medical_aptitude_certificate_filename': cv_digital_id.medical_aptitude_certificate_filename,
                    'is_victim_violent': cv_digital_id.is_victim_violent,
                    'relationship_victim_violent_file': cv_digital_id.relationship_victim_violent_file,
                    'relationship_victim_violent_filename': cv_digital_id.relationship_victim_violent_filename,
                    'is_public_information_victim_violent': cv_digital_id.is_public_information_victim_violent,
                    'cv_address_street_id': cv_digital_id.cv_address_street_id.id,
                    'cv_address_street2_id': cv_digital_id.cv_address_street2_id.id,
                    'cv_address_street3_id': cv_digital_id.cv_address_street3_id.id,
                    'allow_content_public': cv_digital_id.allow_content_public,
                    'situation_disability': cv_digital_id.situation_disability,
                    'people_disabilitie': cv_digital_id.people_disabilitie,
                    'document_certificate_file': cv_digital_id.document_certificate_file,
                    'document_certificate_filename': cv_digital_id.document_certificate_filename,
                    'certificate_date': cv_digital_id.certificate_date,
                    'to_date': cv_digital_id.to_date,
                    'see': cv_digital_id.see,
                    'hear': cv_digital_id.hear,
                    'walk': cv_digital_id.walk,
                    'speak': cv_digital_id.speak,
                    'realize': cv_digital_id.realize,
                    'lear': cv_digital_id.lear,
                    'interaction': cv_digital_id.interaction,
                    'need_other_support': cv_digital_id.need_other_support,
                })

    def _20_10_vdl_seccions_ps07_12168_seccions(self, limit=10000, offset=0):
        FIELDS_TO_APPLY_INEMPLOYEE = [
            'cv_gender_id',
            'cv_gender2',
            'gender_date',
            'cv_gender_record_file',
            'cv_gender_record_filename',
            'is_cv_gender_public',
            'cv_race_ids',
            'cv_race2',
            'cv_first_race_id',
            'is_cv_race_public',
            'is_afro_descendants',
            'afro_descendants_file',
            'afro_descendants_filename',
            'afro_descendant_date',
            'is_victim_violent',
            'relationship_victim_violent_file',
            'relationship_victim_violent_filename',
        ]
        CVDigital = self.env['onsc.cv.digital'].sudo()
        cvs = CVDigital.search([('is_docket_active', '=', True), ('employee_id', '!=', False), ('type', '=', 'cv')],
                               limit=limit, offset=offset)
        _logger.info("******** 20.10 VDL INICIO **********")
        _logger.info("******** 20.10 VDL LIMIT %s **********" % (str(limit)))
        _logger.info("******** 20.10 VDL OFFSET %s **********" % (str(offset)))
        _logger.info("CVS: %s" % (str(cvs.ids)))
        for cv in cvs:
            values = {}
            for _field in FIELDS_TO_APPLY_INEMPLOYEE:
                if _field == 'cv_race_ids':
                    cv_race_ids = [(5,)]
                    for cv_race_id in getattr(cv, _field):
                        cv_race_ids.append((4, cv_race_id.id))
                    values[_field] = cv_race_ids
                elif "_id" in _field:
                    values[_field] = getattr(cv, _field).id
                else:
                    values[_field] = getattr(cv, _field)
            cv.employee_id.suspend_security().write(values)
        _logger.info("******** 20.10 VDL FIN **********")

    def _20_10_vdl_seccions_ps07_12168_vdl_state(self, limit=10000, offset=0):
        _logger.info("******** 20.10 VDL STATE INICIO **********")
        _logger.info("******** 20.10 VDL LIMIT %s **********" % (str(limit)))
        _logger.info("******** 20.10 VDL OFFSET %s **********" % (str(offset)))
        CVDigital = self.env['onsc.cv.digital'].sudo()
        cvs = CVDigital.search([
            ('is_docket_active', '=', True),
            ('employee_id', '!=', False),
            ('type', '=', 'cv'),
            ('legajo_gral_info_documentary_validation_state', '!=', 'to_validate')
        ], limit=limit, offset=offset)
        cvs.with_context(ignore_base_restrict=True).button_legajo_update_documentary_validation_sections_tovalidate()
        _logger.info("******** 20.10 VDL STATE FIN **********")
