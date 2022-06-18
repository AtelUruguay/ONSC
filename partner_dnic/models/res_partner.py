# -*- coding: utf-8 -*-
import logging

from unidecode import unidecode

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError
from ..soap import dnic_client

_logger = logging.getLogger(__name__)


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

        result = {}

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

    def update_dnic_values(self, jump_error=False):
        """
        Actualiza los valores del partner consultando al servicio de dnic
        (Si el flag is_dnic_integrated está activo)
        :param jump_error: Si está en true se realiza un commit antes de consultar el servicio para no perder datos
        si el mismo da error
        :return: boolean
        """
        if self.env.company.is_dnic_integrated:
            self = self.filtered(lambda x: x.is_cv_uruguay)
            if self:
                # Preservamos desde este punto ppor si falla el servicio
                with self._cr.savepoint():
                    try:
                        client_obj = dnic_client.DNICClient(self.env.company)
                        for rec in self:
                            response = client_obj.ObtPersonaPorDoc(rec.cv_nro_doc)
                            values = self.get_cv_main_values()
                            values.update({
                                'cv_dnic_full_name': response.get('cv_dnic_full_name', ''),
                                'cv_dnic_name_1': response.get('cv_dnic_name_1', ''),
                                'cv_dnic_name_2': response.get('cv_dnic_name_2', ''),
                                'cv_dnic_lastname_1': response.get('cv_dnic_lastname_1', ''),
                                'cv_dnic_lastname_2': response.get('cv_dnic_lastname_2', ''),
                                'cv_last_name_adoptive_1': response.get('cv_last_name_adoptive_1', ''),
                                'cv_last_name_adoptive_2': response.get('cv_last_name_adoptive_2', ''),
                            })
                            return rec.with_context(can_update_contact_cv=True).write(values)
                    except Exception as e:
                        _logger.error(_('Ha ocurrido un error al tratar de consultar el servicio de DNIC'))
                        _logger.error(_('Error encontrado: %s' % e))
                        if not jump_error:
                            raise ValidationError(
                                _('Ha ocurrido un error al consultar el servicio de DNIC. %s' % e))

        return False

    @api.model
    def _run_retry_dnic_cron(self):
        """
        Cron que identifica los partner de Uruguay que no
        :return:
        """
        if self.env.company.is_dnic_integrated:
            partner_to_fix = self.env['res.partner'].search([
                ('is_partner_cv', '=', True),
                ('cv_dnic_name_1', '=', False),
            ]).filtered(lambda x: x.is_cv_uruguay)
            partner_to_fix.update_dnic_values()
            _logger.info("Se procesaron los siguientes Partner de CV: %s" % partner_to_fix.ids)
