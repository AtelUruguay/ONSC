# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tests.common import new_test_user


@tagged('onsc')
class ONSCCVDigitalCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(ONSCCVDigitalCommon, cls).setUpClass()
        cls.user_cv = new_test_user(cls.env, login='group_user_cv',
                                    groups='onsc_cv_digital.group_user_cv')
        cls.gestor_catalogos_cv = new_test_user(cls.env, login='gestor_catalogos_cv',
                                                groups='onsc_cv_digital.group_gestor_catalogos_cv')
        cls.validador_catalogos_cv = new_test_user(cls.env, login='group_validador_catalogos_cv',
                                                   groups='onsc_cv_digital.group_validador_catalogos_cv')
        today = date.today()
        cls.partner_user_cv = cls.user_cv.partner_id.with_context(can_update_contact_cv=True)

        cls.partner_user_cv.write({
            'cv_emissor_country_id': cls.env.ref('base.uy').id,
            'cv_document_type_id': cls.env.ref('onsc_cv_digital.onsc_cv_document_type_1').id,
            'cv_nro_doc': '66666',
            'cv_first_name': 'USER CV',
            'cv_birthdate': today + relativedelta(years=35),
            'cv_sex': 'male',
            'cv_expiration_date': today + relativedelta(years=2),
            'is_company': False,
            'is_partner_cv': True,
        })

        cls.partner_gestor_cv = cls.gestor_catalogos_cv.partner_id.with_context(can_update_contact_cv=True)
        cls.partner_gestor_cv.write({
            'cv_emissor_country_id': cls.env.ref('base.uy').id,
            'cv_document_type_id': cls.env.ref('onsc_cv_digital.onsc_cv_document_type_1').id,
            'cv_nro_doc': '77777',
            'cv_first_name': 'GESTOR CV',
            'cv_birthdate': today - relativedelta(years=27),
            'cv_sex': 'feminine',
            'cv_expiration_date': today + relativedelta(years=1),
            'is_company': False,
            'is_partner_cv': True,
        })

        cls.partner_validador_cv = cls.validador_catalogos_cv.partner_id.with_context(can_update_contact_cv=True)
        cls.partner_validador_cv.write({
            'cv_emissor_country_id': cls.env.ref('base.uy').id,
            'cv_document_type_id': cls.env.ref('onsc_cv_digital.onsc_cv_document_type_1').id,
            'cv_nro_doc': '88888',
            'cv_first_name': 'VALIDADOR CV',
            'cv_birthdate': today - relativedelta(years=21),
            'cv_sex': 'feminine',
            'cv_expiration_date': today + relativedelta(years=2),
            'is_company': False,
            'is_partner_cv': True,
        })
