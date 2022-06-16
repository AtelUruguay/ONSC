# -*- coding: utf-8 -*-
from odoo import fields, models
from ..soap import dnic_client
from unidecode import unidecode


def compare_string_without_consider_accents(str1='', str2=''):
    """
    Compara dos strings ignorando casos sensitivos y acentos
    :param str1:
    :param str2:
    :return:
    """
    upper_str1 = unidecode(str1.upper())
    upper_str2 = unidecode(str2.upper())
    return upper_str1 == upper_str2


class ResPartner(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.partner'

    cv_dnic_full_name = fields.Char(u'Nombre en cédula')
    cv_dnic_name_1 = fields.Char(u'Primer nombre CI')
    cv_dnic_name_2 = fields.Char(u'Segundo nombre CI')
    cv_dnic_lastname_1 = fields.Char(u'Primer apellido CI')
    cv_dnic_lastname_2 = fields.Char(u'Segundo apellido CI')
    cv_last_name_adoptive_1 = fields.Char(u'Primer apellido adoptivo')
    cv_last_name_adoptive_2 = fields.Char(u'Segundo apellido adoptivo')

    def get_cv_main_values(self, response):
        "Metodo que arma el diccionario los valores correspondientes a actualizar de ID digital "

        self.ensure_one()

        name_values = [self.cv_first_name,
                       self.cv_second_name,
                       self.cv_last_name_1,
                       self.cv_last_name_2]
        cv_full_name = ' '.join([x for x in name_values if x])
        # Caso 1: Ambos Nombres y Apellidos coinciden con nombre en cédula
        if compare_string_without_consider_accents(cv_full_name, response.get('cv_dnic_full_name')):
            pass

    def update_dnic_values(self):
        if self.env.company.is_dnic_integrated:
            self = self.filtered(lambda x: x.is_cv_uruguay)
            if self:
                client_obj = dnic_client.DNICClient()
                for rec in self:
                    response = client_obj.obtDocDigitalizadoService(rec.cv_nro_doc)
                    values = self.get_cv_main_values()
                    return rec.with_context(can_update_contact_cv=True).write({
                        'cv_dnic_full_name': response.get('cv_dnic_full_name', ''),
                        'cv_dnic_name_1': response.get('cv_dnic_name_1', ''),
                        'cv_dnic_name_2': response.get('cv_dnic_name_2', ''),
                        'cv_dnic_lastname_1': response.get('cv_dnic_lastname_1', ''),
                        'cv_dnic_lastname_2': response.get('cv_dnic_lastname_2', ''),
                        'cv_last_name_adoptive_1': response.get('cv_last_name_adoptive_1', ''),
                        'cv_last_name_adoptive_2': response.get('cv_last_name_adoptive_2', ''),
                    })

        return False
