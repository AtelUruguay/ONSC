# -*- coding: utf-8 -*-
import uuid

from odoo.addons.onsc_cv_digital.models.catalogs.res_partner import calc_full_name
from odoo.addons.onsc_cv_digital.tests.common import ONSCCVDigitalCommon

from odoo.tests import tagged


@tagged('onsc')
class TestResPartner(ONSCCVDigitalCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.cv_dnic_name_1 = 'Nombre 1'
        cls.cv_dnic_name_2 = 'Nombre 2'
        cls.cv_dnic_lastname_1 = 'Apellido 1'
        cls.cv_dnic_lastname_2 = 'Apellido 2'
        cls.cv_last_name_adoptive_1 = 'Adoptivo 1'
        cls.cv_last_name_adoptive_2 = 'Adoptivo 2'

    @classmethod
    def construct_partner_and_expected_result(cls, name1, name2,
                                              last_name1, last_name2,
                                              dnic_full_name,
                                              last_name_adoptive1='',
                                              last_name_adoptive2='', ):
        partner_cv = cls.partner_user_cv.copy(
            {
                'cv_nro_doc': uuid.uuid1(),
                'cv_dnic_name_1': name1,
                'cv_dnic_name_2': name2,
                'cv_dnic_lastname_1': last_name1,
                'cv_dnic_lastname_2': last_name2,
                'cv_dnic_full_name': dnic_full_name,
                'cv_last_name_adoptive_1': last_name_adoptive1,
                'cv_last_name_adoptive_2': last_name_adoptive2,
            }
        )
        result_expected = {
            'cv_first_name': name1,
            'cv_second_name': name2,
            'cv_last_name_1': last_name1,
            'cv_last_name_2': last_name2,
            'cv_source_info_auth_type': 'dnic'
        }
        return partner_cv, result_expected

    def test_dnic_update_iddigital_case1(cls):
        "Ambos Nombres y Apellidos coinciden con nombre en cédula"
        dnic_full_name = calc_full_name(cls.cv_dnic_name_1, cls.cv_dnic_name_2,
                                        cls.cv_dnic_lastname_1, cls.cv_dnic_lastname_2)
        partner_cv, result_expected = cls.construct_partner_and_expected_result(
            cls.cv_dnic_name_1,
            cls.cv_dnic_name_2,
            cls.cv_dnic_lastname_1,
            cls.cv_dnic_lastname_2,
            dnic_full_name
        )
        result = partner_cv.get_cv_main_values()
        cls.assertDictEqual(result, result_expected)

    def test_dnic_update_iddigital_case1_b(cls):
        # Caso 1.b: Apellido1 nulo
        dnic_full_name = calc_full_name(cls.cv_dnic_name_1, cls.cv_dnic_name_2,
                                        '', cls.cv_dnic_lastname_2)
        partner_cv, result_expected = cls.construct_partner_and_expected_result(
            cls.cv_dnic_name_1,
            cls.cv_dnic_name_2,
            '',
            cls.cv_dnic_lastname_2,
            dnic_full_name
        )
        result = partner_cv.get_cv_main_values()

        result_expected.update({'cv_last_name_1': result_expected.get('cv_last_name_2'),
                                'cv_last_name_2': result_expected.get('cv_last_name_1')})

        cls.assertDictEqual(result, result_expected)

    def test_dnic_update_iddigital_case2(cls):
        # Caso 2: Apellidos cambiados de orden
        dnic_full_name = calc_full_name(cls.cv_dnic_name_1, cls.cv_dnic_name_2,
                                        cls.cv_dnic_lastname_2, cls.cv_dnic_lastname_1)
        partner_cv, result_expected = cls.construct_partner_and_expected_result(
            cls.cv_dnic_name_1,
            cls.cv_dnic_name_2,
            cls.cv_dnic_lastname_1,
            cls.cv_dnic_lastname_2,
            dnic_full_name
        )
        result = partner_cv.get_cv_main_values()
        result_expected.update({'cv_last_name_1': result_expected.get('cv_last_name_2'),
                                'cv_last_name_2': result_expected.get('cv_last_name_1')})
        cls.assertDictEqual(result, result_expected)

    def test_dnic_update_iddigital_case3(cls):
        # Caso 3: Apellidos adoptivos en nombre en cédula
        dnic_full_name = calc_full_name(cls.cv_dnic_name_1, cls.cv_dnic_name_2,
                                        cls.cv_last_name_adoptive_1, cls.cv_last_name_adoptive_2)
        partner_cv, result_expected = cls.construct_partner_and_expected_result(
            cls.cv_dnic_name_1,
            cls.cv_dnic_name_2,
            last_name1='',
            last_name2='',
            dnic_full_name=dnic_full_name,
            last_name_adoptive1=cls.cv_last_name_adoptive_1,
            last_name_adoptive2=cls.cv_last_name_adoptive_2,
        )
        result = partner_cv.get_cv_main_values()
        result_expected.update({'cv_last_name_1': cls.cv_last_name_adoptive_1,
                                'cv_last_name_2': cls.cv_last_name_adoptive_2})
        cls.assertDictEqual(result, result_expected)
