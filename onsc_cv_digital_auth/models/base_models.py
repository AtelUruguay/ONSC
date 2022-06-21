# -*- coding: utf-8 -*-

from unidecode import unidecode

from odoo import models, api

DNIC_FROZEN_COLUMNS = [
    'cv_dnic_name_1',
    'cv_dnic_name_2',
    'cv_dnic_lastname_1',
    'cv_dnic_lastname_2',
    'cv_last_name_adoptive_1',
    'cv_last_name_adoptive_2',
]


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


class ResUsers(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.users'

    @api.model
    def _prepare_userinfo_dict(self, provider, params):
        result = super(ResUsers, self)._prepare_userinfo_dict(provider, params)
        nickname = params.get('nickname', False)
        doc_type = self.env['onsc.cv.document.type'].search(
            [('code', '=', nickname.split('-')[1])], limit=1)
        result.update({
            'cv_emissor_country_id': result.get('country_id', False),
            'cv_first_name': params.get('primer_nombre', False),
            'cv_second_name': params.get('segundo_nombre', False),
            'cv_last_name_1': params.get('primer_apellido', False),
            'cv_last_name_2': params.get('segundo_apellido', False),
            'cv_document_type_id': doc_type.id,
            'cv_nro_doc': params.get('numero_documento', False),
            'is_partner_cv': True
        })
        return result

    @api.model
    def _get_user(self, provider, params):
        oauth_user = super(ResUsers, self.with_context(can_update_contact_cv=True))._get_user(provider, params)
        # LLamada al servicio de DNIC
        oauth_user.partner_id.update_dnic_values(jump_error=True)
        return oauth_user


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_frozen_columns(self):
        "Sobreescrito para incorporar las columnas DNIC como de no modificacion"
        return super(ResPartner, self)._get_frozen_columns() + DNIC_FROZEN_COLUMNS

    @api.depends('is_partner_cv', 'cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2',
                 'cv_dnic_name_1', 'cv_dnic_name_2', 'cv_dnic_lastname_1', 'cv_dnic_lastname_2')
    def _compute_cv_full_name(self):
        "Sobreescrito para agregar campos en el api depends"
        super(ResPartner, self)._compute_cv_full_name()

    def button_update_dnic_values(self):
        self.update_dnic_values()

    def get_cv_main_values(self, response):
        "Metodo que arma el diccionario los valores correspondientes a actualizar de ID digital "
        self.ensure_one()

        result = super(ResPartner, self).get_cv_main_values(response)

        def calc_full_name(cv_first_name, cv_second_name, cv_last_name_1, cv_last_name_2):
            name_values = [cv_first_name,
                           cv_second_name,
                           cv_last_name_1,
                           cv_last_name_2]
            return ' '.join([x for x in name_values if x])

        cv_full_name = calc_full_name(
            self.cv_first_name,
            self.cv_second_name,
            self.cv_last_name_1,
            self.cv_last_name_2)

        # Caso 1: Ambos Nombres y Apellidos coinciden con nombre en cédula
        if compare_string_without_consider_accents(cv_full_name, response.get('cv_dnic_full_name')):
            # Caso 1.b: Apellido1 nulo
            if (not self.cv_last_name_1 and self.cv_last_name_2):
                result.update({
                    'cv_last_name_1': self.cv_last_name_2,
                    'cv_last_name_2': self.cv_last_name_1,
                })
        else:
            cv_full_name = calc_full_name(self.cv_first_name, self.cv_second_name, self.cv_last_name_2,
                                          self.cv_last_name_1)
            # Caso 2: Apellidos cambiados de orden
            if compare_string_without_consider_accents(cv_full_name, response.get('cv_dnic_full_name')):
                result.update({
                    'cv_last_name_1': self.cv_last_name_2,
                    'cv_last_name_2': self.cv_last_name_1,
                })
            else:
                cv_last_name_adoptive_1 = response.get('cv_last_name_adoptive_1', '')
                cv_last_name_adoptive_2 = response.get('cv_last_name_adoptive_2', '')
                if cv_last_name_adoptive_1 or cv_last_name_adoptive_2:
                    cv_full_name = calc_full_name(self.cv_first_name, self.cv_second_name, cv_last_name_adoptive_1,
                                                  cv_last_name_adoptive_2)
                    # Caso 3: Apellidos adoptivos en nombre en nombre en cédula
                    if compare_string_without_consider_accents(cv_full_name, response.get('cv_dnic_full_name')):
                        result.update({
                            'cv_last_name_1': cv_last_name_adoptive_1,
                            'cv_last_name_2': cv_last_name_adoptive_2,
                        })
        return result
